import urllib
import logging


class TypeConverter(object):
    @staticmethod
    def _str(x):
        return urllib.unquote(x).decode('utf8')

    @staticmethod
    def _float(x):
        try:
            return float(x)
        except:
            return 0.0

    @staticmethod
    def _int(x):
        try:
            return int(x)
        except:
            return 0

    @staticmethod
    def _bool(x):
        try:
            return bool(int(x))
        except:
            return None

    @staticmethod
    def convert(element, schema):
        types = {
            "number": TypeConverter._float,
            "integer": TypeConverter._int,
            "string": TypeConverter._str,
            "boolean": TypeConverter._bool,
        }

        if not element:
            return {}

        if not isinstance(element, dict):
            logging.error("%s is not a dictionary", element)
            return {}

        for field_name, value in element.items():
            field_schema = schema.properties.get(field_name)

            if not field_schema:
                continue

            field_type = field_schema.type[0] if isinstance(field_schema.type, list) else field_schema.type

            if field_type in types:
                element[field_name] = types[field_type](value)
                continue

            if field_type == "array":
                if not value:
                    element[field_name] = []
                    continue

                if not isinstance(value, list):
                    logging.error("%s: %s is not a list", field_name, value)
                    element[field_name] = []
                    continue

                for index, _value in enumerate(value):
                    value[index] = TypeConverter.convert(_value, field_schema.get("items"))

                element[field_name] = value

                continue

            if field_type == "object":
                element[field_name] = TypeConverter.convert(value, field_schema)

        return element
