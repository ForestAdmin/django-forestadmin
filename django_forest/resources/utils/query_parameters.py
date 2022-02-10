import re
from collections import defaultdict

DICT_RE = r"^(?P<field>\w+)\[(?P<subfield>\w+)\]$"


def parse_value(value):
    if ',' in value:
        return value.split(',')
    return value

def parse_qs(parameters):
    qs = defaultdict(dict)
    for key, value in parameters.items():
        m = re.search(DICT_RE, key)
        parsed_value = parse_value(value)
        if m:
            groups = m.groupdict()
            qs[groups['field']][groups['subfield']] = parsed_value
        else:
            qs[key] = parsed_value

    return qs
