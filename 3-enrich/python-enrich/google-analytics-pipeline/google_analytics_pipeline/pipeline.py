from __future__ import print_function

import json
from datetime import date

import apache_beam as beam
from bunch import bunchify

from .core.transform.parse_logs import ParseLogsFn
from .core.transform.map_protocol import MapMeasurementProtocolFn
from .core.transform.type_conversion import TypeConversionFn
from .core.transform.schema_validation import SchemaValidationFn
from .core.transform.enforce_schema import EnforceSchemaFn

from .core.enrichment.device import DeviceEnrichmentFn
from .core.enrichment.page import PageEnrichmentFn
from .core.enrichment.referrer import ReferrerEnrichmentFn
from .core.enrichment.geo_network import GeoNetworkEnrichmentFn
from .core.enrichment.utm import UTMParamsEnrichmentFn

from .utils.bigquery import jsonschema_to_bq_schema

from apache_beam.io.gcp.bigquery import parse_table_schema_from_json, BigQueryDisposition


class GoogleAnalyticsPipeline:
    def __init__(self, pipeline, client_config, app_config):
        self.pipeline = pipeline
        self.client_config = client_config
        self.app_config = app_config

    def _load_protocol_config(self):
        config_file_path = self.app_config.protocol_config.format(project_root=self.app_config.project_root)

        with open(config_file_path, "r") as f:
            self.protocol_config = bunchify(json.load(f))

    def _load_event_model_schema(self):
        schema_repo = self.app_config.schema_repo.format(project_root=self.app_config.project_root)
        file_path = "%s/%s" % (schema_repo, self.app_config.raw_event_model_schema)

        with open(file_path, "r") as f:
            self.raw_event_model_schema = bunchify(json.load(f))

        file_path = "%s/%s" % (schema_repo, self.app_config.enriched_event_model_schema)

        with open(file_path, "r") as f:
            self.enriched_event_model_schema = bunchify(json.load(f))

    def _get_bq_schema(self, event_model_schema):
        schema = jsonschema_to_bq_schema(event_model_schema)
        schema = {"fields": schema}
        return parse_table_schema_from_json(json.dumps(schema))

    def run(self):
        self._load_protocol_config()
        self._load_event_model_schema()

        # Read from Cloud PubSub Topic
        request_logs = self.pipeline | beam.io.ReadFromPubSub(topic=self.client_config.collector_topic)

        # Parse logs
        logs = request_logs | beam.ParDo(ParseLogsFn())

        # Map to Google Analytics measurement protocol
        logs = logs | beam.ParDo(MapMeasurementProtocolFn(self.protocol_config))

        # Type conversion as per event model schema
        logs = logs | beam.ParDo(TypeConversionFn(self.raw_event_model_schema))

        # Schema validation
        logs = logs | beam.ParDo(SchemaValidationFn(self.raw_event_model_schema))

        # Write raw event model to BigQuery
        raw_event_model_dataset = self.client_config.raw_event_model_dataset
        raw_event_model_table_prefix = self.client_config.raw_event_model_table_prefix
        table_name = raw_event_model_table_prefix + date.today().strftime("%Y%m%d")
        raw_schema = self._get_bq_schema(self.raw_event_model_schema)
        project_id = self.client_config.project_id

        logs | "raw-events-to-bigquery" >> beam.io.WriteToBigQuery(
            table_name, raw_event_model_dataset, project_id, raw_schema
        )

        # Device info enrichment
        logs = logs | beam.ParDo(DeviceEnrichmentFn())

        # Page info enrichment
        logs = logs | beam.ParDo(PageEnrichmentFn())

        # Referrer info enrichment
        logs = logs | beam.ParDo(ReferrerEnrichmentFn())

        # Geo network enrichment
        logs = logs | beam.ParDo(GeoNetworkEnrichmentFn())

        # UTM parameters enrichment
        logs = logs | beam.ParDo(UTMParamsEnrichmentFn())

        # Enforce schema to remove raw fields
        logs = logs | beam.ParDo(EnforceSchemaFn(self.enriched_event_model_schema))

        # Write enriched event model to BigQuery
        enriched_event_model_dataset = self.client_config.enriched_event_model_dataset
        enriched_event_model_table_prefix = self.client_config.enriched_event_model_table_prefix
        table_name = enriched_event_model_table_prefix + date.today().strftime("%Y%m%d")
        enriched_schema = self._get_bq_schema(self.enriched_event_model_schema)
        project_id = self.client_config.project_id

        logs | "enriched-events-to-bigquery" >> beam.io.WriteToBigQuery(
            table_name, enriched_event_model_dataset, project_id, enriched_schema,
            # write_disposition=BigQueryDisposition.WRITE_TRUNCATE  # @TODO remove this option later
        )

        logs | "write-to-text" >> beam.Map(print)
