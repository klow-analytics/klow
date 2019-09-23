import apache_beam as beam
import logging

from urlparse import urlparse, parse_qs

from ...utils.helper import deep_get

from referer_parser import Referer


class ReferrerEnrichmentFn(beam.DoFn):
    def process(self, element):
        try:
            referrer_url = deep_get(element, "trafficSource", "documentReferrer")
            referrer_url = referrer_url or deep_get(element, "header", "referrer") or ""

            page_url = deep_get(element, "pageView", "documentLocationUrl") or ""

            referrer = Referer(referrer_url, page_url)

            element["referrer"] = element.get("referrer", {})

            element["referrer"]["source"] = referrer.referer
            element["referrer"]["medium"] = referrer.medium
            element["referrer"]["searchParameter"] = referrer.search_parameter
            element["referrer"]["searchTerm"] = referrer.search_term

            element["referrer"]["hostname"] = referrer.uri.hostname
            element["referrer"]["path"] = referrer.uri.path or "/"
            element["referrer"]["fragment"] = referrer.uri.fragment

            query_params = parse_qs(referrer.uri.query)

            element["referrer"]["queryParams"] = []
            for k, v in query_params.items():
                element["referrer"]["queryParams"].append({
                    "name": k,
                    "value": v[0]
                })

            yield element
        except Exception as e:
            logging.exception(e)
            yield element
