import json
import unittest

from bunch import bunchify
from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.transform.map_protocol import MapMeasurementProtocolFn


@ddt
class TestMapProtocol(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        config_file_path = 'configs/protocol-mapping.json'
        with open(config_file_path, "r") as f:
            self.protocol_config = bunchify(json.load(f))

        self.test_fn = MapMeasurementProtocolFn(self.protocol_config).process

    @file_data("../fixtures/map-protocol-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
