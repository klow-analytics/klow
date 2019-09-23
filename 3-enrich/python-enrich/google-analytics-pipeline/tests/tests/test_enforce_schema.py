import json
import unittest

from bunch import bunchify
from ddt import ddt
from ddt import file_data

from google_analytics_pipeline.core.transform.enforce_schema import EnforceSchemaFn


@ddt
class TestEnforceSchema(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        schema_path = 'tests/fixtures/event-model-schema.json'
        with open(schema_path, "r") as f:
            self.schema = bunchify(json.load(f))

        self.test_fn = EnforceSchemaFn(self.schema).process

    @file_data("../fixtures/enforce-schema-testcases.json")
    def test(self, test_input, expected_output):
        for index, output in enumerate(self.test_fn(test_input)):
            self.assertDictEqual(output, expected_output[index])
