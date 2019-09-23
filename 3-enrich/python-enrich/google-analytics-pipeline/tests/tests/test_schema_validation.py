import json
import unittest

from bunch import bunchify
from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.transform.schema_validation import SchemaValidationFn


@ddt
class TestSchemaValidation(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        schema_path = 'tests/fixtures/event-model-schema.json'
        with open(schema_path, "r") as f:
            self.schema = bunchify(json.load(f))

        self.test_fn = SchemaValidationFn(self.schema).process

    @file_data("../fixtures/schema-validation-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
