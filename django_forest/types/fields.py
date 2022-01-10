from dataclasses import field
from django.db import models
from django.contrib.postgres import fields as ps_fields

from django_forest.common.types import FieldTypes

TYPE_CHOICES = {
    models.AutoField: FieldTypes.INTEGER,
    models.BigAutoField: FieldTypes.INTEGER,
    models.BinaryField: FieldTypes.STRING,
    models.BooleanField: FieldTypes.BOOLEAN,
    models.CharField: FieldTypes.STRING,
    models.DateField: FieldTypes.DATE,
    models.DateTimeField: FieldTypes.DATETIME,
    models.DecimalField: FieldTypes.FLOAT,
    models.DurationField: FieldTypes.NUMBER,
    models.EmailField: FieldTypes.STRING,
    models.FileField: FieldTypes.STRING,
    models.FilePathField: FieldTypes.STRING,
    models.FloatField: FieldTypes.FLOAT,
    models.IntegerField: FieldTypes.INTEGER,
    models.BigIntegerField: FieldTypes.INTEGER,
    models.IPAddressField: FieldTypes.STRING,
    models.GenericIPAddressField: FieldTypes.STRING,
    models.JSONField: FieldTypes.JSON,
    models.NullBooleanField: FieldTypes.BOOLEAN,
    models.PositiveBigIntegerField: FieldTypes.INTEGER,
    models.PositiveIntegerField: FieldTypes.INTEGER,
    models.PositiveSmallIntegerField: FieldTypes.INTEGER,
    models.SlugField: FieldTypes.STRING,
    models.SmallAutoField: FieldTypes.STRING,
    models.SmallIntegerField: FieldTypes.INTEGER,
    models.TextField: FieldTypes.STRING,
    models.TimeField: FieldTypes.TIME,
    models.UUIDField: FieldTypes.STRING,
    # postgres type
    ps_fields.CICharField: FieldTypes.STRING,
    ps_fields.CIEmailField: FieldTypes.STRING,
    ps_fields.CITextField: FieldTypes.STRING,
    ps_fields.HStoreField: FieldTypes.JSON,
}

def _get_type(field):
    return TYPE_CHOICES.get(field.__class__, FieldTypes.UNKNOWN)

def handle_relation_field(field):
    if field.target_field.is_relation:
        # usefull when the OneToOneField is also the model primary key
        return handle_relation_field(field.target_field)
    return _get_type(field.target_field)

def handle_many_type(field_type):

    if field_type != FieldTypes.UNKNOWN:
        return [field_type.value]
    return field_type.value


def get_type(field):
    # See connection.data_types (different for each DB Engine)
    # ForestAdmin does not handle range models: https://www.postgresql.org/docs/9.3/rangetypes.html
    # 'RangeField'
    # 'IntegerRangeField'
    # 'BigIntegerRangeField'
    # 'DecimalRangeField'
    # 'DateTimeRangeField'
    # 'DateRangeField'
    
    is_many = False
    django_type = field.__class__
    if field.is_relation:
        forest_type = handle_relation_field(field)
        is_many = field.one_to_many or field.many_to_many
    elif django_type == ps_fields.ArrayField:
        # nested arrayfield are not handled
        forest_type = _get_type(field.base_field)
        is_many = True
    elif hasattr(field, "choices") and field.choices is not None:
        forest_type = FieldTypes.ENUM
    else:
        forest_type = _get_type(field)
    
    if is_many:
        return handle_many_type(forest_type)
    else:
        return forest_type.value
