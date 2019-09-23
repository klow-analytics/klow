import apache_beam as beam


class EnforceSchemaFn(beam.DoFn):
    def __init__(self, schema):
        super(EnforceSchemaFn, self).__init__()

        self.schema = schema

    def _enforce_schema(self, element, schema):
        _element = {}
        if not element:
            return _element

        if not isinstance(element, dict):
            return _element

        for field_name, value in element.items():
            field_schema = schema.properties.get(field_name)

            if not field_schema:
                continue

            field_type = field_schema.type[0] if isinstance(field_schema.type, list) else field_schema.type

            if field_type == "array":
                if not value:
                    _element[field_name] = []
                    continue

                if not isinstance(value, list):
                    _element[field_name] = []
                    continue

                for index, _value in enumerate(value):
                    value[index] = self._enforce_schema(_value, field_schema.get("items"))

                _element[field_name] = value

            elif field_type == "object":
                _element[field_name] = self._enforce_schema(value, field_schema)
            else:
                _element[field_name] = value

        return _element

    def process(self, element):

        yield self._enforce_schema(element, self.schema)
