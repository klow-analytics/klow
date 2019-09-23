import apache_beam as beam
import logging
import json


class ParseLogsFn(beam.DoFn):
    def process(self, element):
        try:
            element = element.decode('utf-8')
            element = json.loads(element)
            log = json.loads(element.get("textPayload"))

            if not log:
                raise ValueError("Log is empty or corrupted")

            _element = {}
            for k, v in log.items():
                if isinstance(v, dict):
                    for _k, _v in v.items():
                        _element[_k.lower()] = _v[0] if isinstance(_v, list) else _v
                else:
                    _element[k.lower()] = v[0] if isinstance(v, list) else v

            yield _element

        except Exception as e:
            logging.exception(e)
