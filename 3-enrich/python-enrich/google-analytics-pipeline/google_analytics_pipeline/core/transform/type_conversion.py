import apache_beam as beam
import logging
from ...utils.type_converter import TypeConverter


class TypeConversionFn(beam.DoFn):
    def __init__(self, schema):
        super(TypeConversionFn, self).__init__()

        self.schema = schema

    def process(self, element):
        try:
            yield TypeConverter.convert(element, self.schema)

        except Exception as e:
            logging.exception(e)
