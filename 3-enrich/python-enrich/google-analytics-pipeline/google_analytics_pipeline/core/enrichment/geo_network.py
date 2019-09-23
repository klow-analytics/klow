import apache_beam as beam
import logging
from ...utils.helper import deep_get


class GeoNetworkEnrichmentFn(beam.DoFn):
    def process(self, element):
        try:
            element["geoNetwork"] = element.get("geoNetwork", {})

            element["geoNetwork"]["continent"] = ""
            element["geoNetwork"]["subContinent"] = ""
            element["geoNetwork"]["country"] = deep_get(element, "header", "appEngineCountry")
            element["geoNetwork"]["region"] = deep_get(element, "header", "appEngineRegion")
            element["geoNetwork"]["metro"] = ""
            element["geoNetwork"]["city"] = deep_get(element, "header", "appEngineCity")

            lat_long = deep_get(element, "header", "appEngineCityLatLong")

            if lat_long:
                latitude, longitude = lat_long.split(",")
                element["geoNetwork"]["latitude"] = latitude
                element["geoNetwork"]["longitude"] = longitude
            else:
                element["geoNetwork"]["latitude"] = None
                element["geoNetwork"]["longitude"] = None

            yield element
        except Exception as e:
            logging.exception(e)
            yield element
