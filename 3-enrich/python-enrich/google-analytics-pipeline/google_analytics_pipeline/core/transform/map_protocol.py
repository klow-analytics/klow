import apache_beam as beam
import logging
import re


class MapMeasurementProtocolFn(beam.DoFn):
    def __init__(self, protocol_config):
        super(MapMeasurementProtocolFn, self).__init__()
        self.protocol_config = protocol_config

    def _check_follow_index_group(self, match_groups, field_group, value):
        for match_group in match_groups:
            if field_group[match_group] != value[match_group]:
                return False
        return True

    def process(self, element):
        try:
            _element = {}

            for field in element:
                # Map simple fields to protocol
                protocol = self.protocol_config.simple_fields.get(field)

                if protocol:
                    field_group = _element.get(protocol.field_group, {})
                    field_group[protocol.field_name] = element[field]
                    _element[protocol.field_group] = field_group
                    continue

                # Map complex indexed fields to protocol
                for p in self.protocol_config.indexed_fields:
                    match = re.match(p, field)
                    if not match:
                        continue

                    protocol = self.protocol_config.indexed_fields[p]
                    field_group = _element.get(protocol.field_group, [])

                    value = {}
                    for index, match_group in enumerate(protocol.match_groups):
                        value[match_group] = match.group(index + 1)

                    value[protocol.field_name] = element[field]

                    if protocol.follow_index:
                        found = False
                        for _field_group in field_group:
                            if self._check_follow_index_group(protocol.match_groups, _field_group, value):
                                _field_group.update(value)
                                found = True
                                break
                        if not found:
                            field_group.append(value)

                    else:
                        field_group.append(value)

                    _element[protocol.field_group] = field_group

            yield _element
        except Exception as e:
            logging.exception(e)
