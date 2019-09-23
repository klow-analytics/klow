import json
import unittest

from bunch import bunchify
from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.transform.type_conversion import TypeConversionFn


@ddt
class TestTypeConverter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        schema_path = 'tests/fixtures/event-model-schema.json'
        with open(schema_path, "r") as f:
            self.schema = bunchify(json.load(f))

        self.test_fn = TypeConversionFn(self.schema).process

    @file_data("../fixtures/type-converter-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
