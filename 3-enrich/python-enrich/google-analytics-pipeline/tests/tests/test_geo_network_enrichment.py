import unittest

from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.enrichment.geo_network import GeoNetworkEnrichmentFn


@ddt
class TestGeoNetworkEnrichment(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.test_fn = GeoNetworkEnrichmentFn().process

    @file_data("../fixtures/geo-network-enrichment-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
