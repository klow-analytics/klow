import apache_beam as beam
import logging

from urlparse import urlparse, parse_qs

from ...utils.helper import deep_get


class PageEnrichmentFn(beam.DoFn):
    def process(self, element):
        try:
            page_url = deep_get(element, "pageView", "documentLocationUrl") or ""

            element["page"] = element.get("page", {})

            element["page"]["title"] = deep_get(element, "pageView", "documentTitle")

            page_url_parsed = urlparse(page_url)
            element["page"]["hostname"] = page_url_parsed.hostname
            element["page"]["path"] = page_url_parsed.path or "/"
            element["page"]["fragment"] = page_url_parsed.fragment

            if element["page"]["path"] != "/":
                for i, path in enumerate(element["page"]["path"][1:].split("/")):
                    element["page"]["pathLevel%d" % (i + 1)] = path

            query_params = parse_qs(page_url_parsed.query)

            element["page"]["queryParams"] = []
            for k, v in query_params.items():
                element["page"]["queryParams"].append({
                    "name": k,
                    "value": v[0]
                })

            yield element
        except Exception as e:
            logging.exception(e)
            yield element
