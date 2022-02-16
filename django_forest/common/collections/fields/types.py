from enum import Enum
from dataclasses import dataclass, field, InitVar, asdict
from typing import Optional, Union, List, Dict

from django_forest.common.collections.fields.validations import (
    FieldValidation,
    ValidationTypes,
    FieldValidationFactory,
)


class FieldTypes(Enum):
    STRING = "String"
    INTEGER = "Integer"
    BOOLEAN = "Boolean"
    DATE = "DateOnly"
    DATETIME = "Date"
    FLOAT = "Float"
    NUMBER = "Number"
    JSON = "Json"
    ENUM = "Enum"
    TIME = "Time"
    UNKNOWN = "unknown"


class RelationhipTypes(Enum):
    HAS_MANY = "HasMany"
    HAS_ONE = "HasOne"
    BELONGS_TO = "BelongsTo"


@dataclass
class Field:
    name: str
    type: FieldTypes
    is_filterable: bool = True
    is_sortable: bool = True
    is_read_only: bool = False
    is_required: bool = False
    default_value: str = None
    reference: str = None
    inverse_of: str = None
    relationship: Optional[RelationhipTypes] = None
    validations: List[FieldValidation] = field(default_factory=list)
    enums: List = field(default_factory=list)
    integration: str = None
    widget: str = None

    is_virtual: bool = field(init=False, default=False)
    is_primary_key: InitVar[bool] = False
    is_autocreated: InitVar[bool] = False

    def __post_init__(self, is_primary_key, is_autocreated) -> None:
        self.is_autocreated = is_autocreated
        self.is_primary_key = is_primary_key
        self.check_relationship()
        self.check_autocreated()
        self.check_validations()

        if self.is_required:
            self.add_present_validation()

    @property
    def is_related_field(self) -> bool:
        return all([self.relationship, self.inverse_of, self.reference])

    def check_autocreated(self) -> None:
        if self.is_autocreated and not self.is_read_only:
            raise ValueError("autocreated field should be read only")

    def check_relationship(self) -> None:
        args = [self.relationship, self.inverse_of, self.reference]
        if not self.is_related_field and any(args):
            raise ValueError(
                "inverse_of, reference and relationship are mandatory for the related fields"
            )

    def check_validations(self) -> None:
        if (self.is_related_field or self.is_read_only) and self.validations:
            raise ValueError(
                "valdiations can't to be apply to related or read_only field"
            )

    def add_present_validation(self):
        self.validations.append(
            FieldValidationFactory.build(ValidationTypes.IS_PRESENT)
        )

    @classmethod
    def serialize_type(cls, field_type: Union[FieldTypes, List[FieldTypes]]) -> str:
        if isinstance(field_type, list):
            return [field_type[0].value]
        return field_type.value

    @classmethod
    def serialize(cls, obj: "Field") -> Dict[str, str]:
        res = asdict(obj)
        res["type"] = cls.serialize_type(obj.type)
        if len(obj.validations) == 0:
            del res["validations"]
        else:
            res["validations"] = [asdict(v) for v in obj.validations]
        if len(obj.enums) == 0:
            del res["enums"]
        if obj.relationship:
            res["relationship"] = obj.relationship.value
        res["field"] = res.pop("name")
        return res
