import unittest

from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.enrichment.page import PageEnrichmentFn


@ddt
class TestPageEnrichment(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.test_fn = PageEnrichmentFn().process

    @file_data("../fixtures/page-enrichment-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
