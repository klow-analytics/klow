import argparse
import json
import os

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from bunch import bunchify

from google_analytics_pipeline.pipeline import GoogleAnalyticsPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-config", dest="client_config", required=True, type=argparse.FileType("r"))
    parser.add_argument("--app-config", dest="app_config", required=True, type=argparse.FileType("r"))

    app_args, pipeline_args = parser.parse_known_args()

    with app_args.client_config as f:
        client_config = bunchify(json.load(f))

    with app_args.app_config as f:
        app_config = bunchify(json.load(f))

    pipeline_options = PipelineOptions(pipeline_args)
    # pipeline_options.view_as(SetupOptions).save_main_session = True
    # pipeline_options.view_as(StandardOptions).streaming = True

    app_config.project_root = os.path.dirname(os.path.realpath(__file__))

    with beam.Pipeline(options=pipeline_options) as p:
        GoogleAnalyticsPipeline(p, client_config, app_config).run()


if __name__ == '__main__':
    main()
