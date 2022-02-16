from django.db import models
from django.contrib.postgres import fields as ps_fields
from django_forest.common.collections.fields.types import FieldTypes


FIELD_TYPES_MAPPING = {
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
