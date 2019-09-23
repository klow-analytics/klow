import apache_beam as beam
import logging

from cerberus import Validator


class SchemaValidationFn(beam.DoFn):
    def __init__(self, schema):
        super(SchemaValidationFn, self).__init__()

        self.schema = self._cerberus_schema(schema)["schema"]

    def _cerberus_schema(self, schema):

        _schema = {
            "type": "dict" if schema["type"] == "object" else schema["type"],
            "schema": schema["properties"].copy()
        }

        for k, v in schema["properties"].items():
            if v.type == "object":
                _schema["schema"][k] = self._cerberus_schema(v)
            elif v.type == "array":
                _schema["schema"][k] = {
                    "type": "list",
                    "schema": self._cerberus_schema(v["items"])
                }
            else:
                _schema["schema"][k] = v

        return _schema

    def process(self, element):
        try:
            validator = Validator(self.schema)

            if not validator.validate(element):
                raise Exception(validator.errors)

            yield element

        except Exception as e:
            logging.exception(e)
