from typing import Any, Optional, Iterable
from django_forest.common.collections.fields.types import (
    FieldTypes,
    Field,
    RelationhipTypes,
)
from django_forest.common.collections.fields.validations import FieldValidation


class FieldFactory:
    @classmethod
    def get_name(cls, field: Any) -> str:
        raise NotImplementedError()

    @classmethod
    def get_type(cls, field: Any) -> FieldTypes:
        raise NotImplementedError()

    @classmethod
    def get_required(cls, field: Any) -> bool:
        return False

    @classmethod
    def get_is_primary_key(cls, field: Any) -> bool:
        return False

    @classmethod
    def get_is_autocreated(cls, field: Any) -> bool:
        return False

    @classmethod
    def get_is_read_only(cls, field: Any) -> bool:
        return cls.get_is_autocreated(field)

    @classmethod
    def get_is_filterable(cls, field: Any) -> bool:
        return True

    @classmethod
    def get_is_sortable(cls, field: Any) -> bool:
        return True

    @classmethod
    def get_default_value(cls, field: Any) -> Optional[str]:
        return None

    @classmethod
    def get_enum_values(cls, field: Any) -> Optional[str]:
        return None

    @classmethod
    def get_reference(cls, field: Any) -> Optional[str]:
        return None

    @classmethod
    def get_relationship(cls, field: Any) -> Optional[str]:
        return None

    @classmethod
    def get_inverse_of(cls, field: Any) -> Optional[str]:
        return None

    @classmethod
    def get_validations(cls, field: Any) -> Optional[Iterable[FieldValidation]]:
        return []

    @classmethod
    def has_many_values(cls, field: Field, original: Any) -> bool:
        return field.relationship == RelationhipTypes.HAS_MANY

    @classmethod
    def build(cls, original: Any) -> Field:
        field = Field(
            name=cls.get_name(original),
            type=cls.get_type(original),
            is_autocreated=cls.get_is_autocreated(original),
            is_required=cls.get_required(original),
            is_read_only=cls.get_is_read_only(original),
            is_primary_key=cls.get_is_primary_key(original),
            is_sortable=cls.get_is_sortable(original),
            is_filterable=cls.get_is_filterable(original),
            relationship=cls.get_relationship(original),
            inverse_of=cls.get_inverse_of(original),
            reference=cls.get_reference(original),
            default_value=cls.get_default_value(original),
            enums=cls.get_enum_values(original),
            validations=cls.get_validations(original),
        )

        if cls.has_many_values(field, original):
            field.type = [field.type]
            print("gooo", field.type)
        return field
