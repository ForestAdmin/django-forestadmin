from typing import Optional, Iterable
from django.db import models
from django.db.models.fields.related import RelatedField as DjRelatedField
from django.contrib.postgres import fields as ps_fields
from django_forest.common.collections.fields.factory import FieldFactory
from django_forest.common.collections.fields.types import (
    Field,
    FieldTypes,
    RelationhipTypes,
)
from django_forest.common.collections.fields.validations import (
    FieldValidation,
    FieldValidationFactory,
)
from django_forest.collections.fields.validations import VALIDATOR_TYPE_MAPPING
from django_forest.collections.fields.types import FIELD_TYPES_MAPPING


class DjangoFieldFactory(FieldFactory):
    @classmethod
    def get_name(cls, field: models.Field) -> str:
        name = None
        try:
            name = field.get_accessor_name()
        except AttributeError:
            name = field.name
        return name

    @classmethod
    def _is_enum(cls, field: Field):
        return hasattr(field, "choices") and field.choices is not None

    @classmethod
    def map_django_type(cls, field: models.Field) -> FieldTypes:
        return FIELD_TYPES_MAPPING.get(field.__class__, FieldTypes.UNKNOWN)

    @classmethod
    def has_many_values(cls, field: Field, original: models.Field) -> bool:
        res = super(DjangoFieldFactory, cls).has_many_values(field, original)
        return res or original.__class__ == ps_fields.ArrayField

    @classmethod
    def get_relationship(cls, field: DjRelatedField) -> RelationhipTypes:
        res = RelationhipTypes.BELONGS_TO
        if field.one_to_many or field.many_to_many:
            res = RelationhipTypes.HAS_MANY
        elif field.one_to_one:
            res = RelationhipTypes.HAS_ONE
        return res

    @classmethod
    def get_related_type(cls, field: models.Field) -> FieldTypes:
        if field.target_field.is_relation:
            # usefull when the OneToOneField is also the model primary key
            return cls.get_related_type(field.target_field)
        return cls.map_django_type(field.target_field)

    @classmethod
    def get_type(cls, field: models.Field) -> FieldTypes:
        forest_type = None

        if field.is_relation:
            forest_type = cls.get_related_type(field)
        elif field.__class__ == ps_fields.ArrayField:
            forest_type = cls.map_django_type(field.base_field)
        elif cls._is_enum(field):
            forest_type = FieldTypes.ENUM
        else:
            forest_type = cls.map_django_type(field)

        return forest_type

    @classmethod
    def get_default_value(cls, field: models.Field) -> Optional[str]:
        default = None
        if hasattr(field, "default") and field.default != models.NOT_PROVIDED:
            default = str(field.default)
        return default

    @classmethod
    def get_required(cls, field: models.Field) -> bool:
        return not (field.blank or field.null) and not cls.get_default_value(field)

    @classmethod
    def get_is_primary_key(cls, field: models.Field) -> bool:
        return hasattr(field, "primary_key") and field.primary_key

    @classmethod
    def get_is_autocreated(cls, field: models.Field) -> bool:
        return hasattr(field, "auto_created") and field.auto_created

    @classmethod
    def get_is_read_only(cls, field: models.Field) -> bool:
        return super().get_is_read_only(field) or field.editable is False

    @classmethod
    def get_enum_values(cls, field: models.Field) -> Optional[str]:
        res = None
        if cls._is_enum(field):
            choices = field.choices
            if field.blank:
                choices = field.get_choices()
            res = [str(c[0]) for c in choices]
        return res

    @classmethod
    def get_reference(cls, field: models.Field) -> Optional[str]:
        res = None
        if field.is_relation:
            res = f"{field.related_model._meta.db_table}.{field.target_field.column}"
        return res

    @classmethod
    def get_inverse_of(cls, field: models.Field) -> Optional[str]:
        res = None
        if field.is_relation:
            res = cls.get_name(field.remote_field)
        return res

    @classmethod
    def get_is_filterable(cls, field: models.Field) -> bool:
        res = super().get_is_filterable(field)
        if (
            field.is_relation
            and cls.get_relationship(field) == RelationhipTypes.HAS_MANY
        ):
            res = False
        return res

    @classmethod
    def get_validations(
        cls, field: models.Field
    ) -> Optional[Iterable[FieldValidation]]:
        res = []
        for validator in field.validators:
            validation_type = VALIDATOR_TYPE_MAPPING.get(validator.__class__)
            if hasattr(validator, "limit_value"):
                limit_value = validator.limit_value
            if validation_type:
                res.append(FieldValidationFactory.build(validation_type, limit_value))
        return res
