import apache_beam as beam

import logging

from urlparse import urlparse, parse_qs

from ...utils.helper import deep_get


class UTMParamsEnrichmentFn(beam.DoFn):
    def process(self, element):
        try:
            page_url = deep_get(element, "pageView", "documentLocationUrl") or ""
            page_url_parsed = urlparse(page_url)
            query_params = parse_qs(page_url_parsed.query)

            traffic_source = element.get("trafficSource", {})

            source = traffic_source.get("campaignSource")
            if not source:
                source = query_params.get("utm_source")[0] if query_params.get("utm_source") else None

            medium = traffic_source.get("campaignMedium")
            if not medium:
                medium = query_params.get("utm_medium")[0] if query_params.get("utm_medium") else None

            term = traffic_source.get("campaignKeyword")
            if not term:
                term = query_params.get("utm_term")[0] if query_params.get("utm_term") else None

            campaign = traffic_source.get("campaignName")
            if not campaign:
                campaign = query_params.get("utm_campaign")[0] if query_params.get("utm_campaign") else None

            content = traffic_source.get("campaignContent")
            if not content:
                content = query_params.get("utm_content")[0] if query_params.get("utm_content") else None

            traffic_source["campaignSource"] = source
            traffic_source["campaignMedium"] = medium
            traffic_source["campaignKeyword"] = term
            traffic_source["campaignName"] = campaign
            traffic_source["campaignContent"] = content

            element["trafficSource"] = traffic_source

            yield element
        except Exception as e:
            logging.exception(e)
            yield element
