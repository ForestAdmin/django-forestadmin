from enum import Enum


class FieldTypes(Enum):
    STRING = "String"
    INTEGER = "Number"
    BOOLEAN = "Boolean"
    DATE = "DateOnly"
    DATETIME = "Date"
    FLOAT = "Number"
    NUMBER = "Number"
    JSON = "Json"
    ENUM = "Enum"
    TIME = "Time"
    UNKNOWN = "unknown"
