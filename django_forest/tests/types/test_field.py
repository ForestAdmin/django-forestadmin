import pytest
from django.db import models
from django.contrib.postgres import fields as ps_fields
from django.test import TestCase

from django_forest.common.types import FieldTypes
from django_forest.types.fields import (
    TYPE_CHOICES,
    _get_type,
    get_type, 
    handle_relation_field,
    handle_many_type
)
from django_forest.tests.models import (
    Restaurant, 
    Place,
    Question,
    Topic,
    Article,
    Publication,
    ChessBoard
)


@pytest.mark.parametrize(
    "mapping",
    (
        (models.AutoField, FieldTypes.INTEGER),
        (models.BigAutoField, FieldTypes.INTEGER),
        (models.BinaryField, FieldTypes.STRING),
        (models.BooleanField, FieldTypes.BOOLEAN),
        (models.CharField, FieldTypes.STRING),
        (models.DateField, FieldTypes.DATE),
        (models.DateTimeField, FieldTypes.DATETIME),
        (models.DecimalField, FieldTypes.FLOAT),
        (models.DurationField, FieldTypes.NUMBER),
        (models.FileField, FieldTypes.STRING),
        (models.FilePathField, FieldTypes.STRING),
        (models.FloatField, FieldTypes.FLOAT),
        (models.IntegerField, FieldTypes.INTEGER),
        (models.BigIntegerField, FieldTypes.INTEGER),
        (models.IPAddressField, FieldTypes.STRING),
        (models.GenericIPAddressField, FieldTypes.STRING),
        (models.JSONField, FieldTypes.JSON),
        (models.NullBooleanField, FieldTypes.BOOLEAN),
        (models.PositiveBigIntegerField, FieldTypes.INTEGER),
        (models.PositiveIntegerField, FieldTypes.INTEGER),
        (models.PositiveSmallIntegerField, FieldTypes.INTEGER),
        (models.SlugField, FieldTypes.STRING),
        (models.SmallAutoField, FieldTypes.STRING),
        (models.SmallIntegerField, FieldTypes.INTEGER),
        (models.TextField, FieldTypes.STRING),
        (models.TimeField, FieldTypes.TIME),
        (models.UUIDField, FieldTypes.STRING),
        (ps_fields.CICharField, FieldTypes.STRING),
        (ps_fields.CIEmailField, FieldTypes.STRING),
        (ps_fields.CITextField, FieldTypes.STRING),
        (ps_fields.HStoreField, FieldTypes.JSON),
    ),
)
def test_type_choices(mapping):
    django_type, forest_type = mapping
    assert TYPE_CHOICES[django_type] == forest_type

@pytest.mark.parametrize("mapping", (
    (Place._meta.get_field("id"), FieldTypes.INTEGER),
    (Restaurant, FieldTypes.UNKNOWN)
))
def test__get_type(mapping):
    field, expected = mapping
    assert _get_type(field) == expected

@pytest.mark.parametrize("mapping", (
    (Restaurant, "place", FieldTypes.INTEGER), 
    (Place, "restaurant", FieldTypes.INTEGER),
    (Question, "topic", FieldTypes.INTEGER),
    (Topic, "question", FieldTypes.INTEGER),
    (Article, "publications", FieldTypes.INTEGER),
    (Publication, "article", FieldTypes.INTEGER)
))
def test_handle_relation_field(mapping):
    model, field_name, field_type = mapping
    assert (
        handle_relation_field(model._meta.get_field(field_name)) == field_type
    )
@pytest.mark.parametrize("mapping", (
    (FieldTypes.UNKNOWN, FieldTypes.UNKNOWN.value),
    (FieldTypes.STRING, [FieldTypes.STRING.value]),
    (FieldTypes.INTEGER, [FieldTypes.INTEGER.value])
))
def test_handle_many_type(mapping):
    field_type, expected = mapping
    assert handle_many_type(field_type) == expected

@pytest.mark.parametrize("mapping",(
    (Place._meta.get_field("id"), FieldTypes.INTEGER.value),
    (Restaurant._meta.get_field("place"), FieldTypes.INTEGER.value),
    (ps_fields.ArrayField(
        ps_fields.ArrayField(
            models.CharField(max_length=10, blank=True),
            size=8,
        ),
        size=8,
    ), FieldTypes.UNKNOWN.value),
    (ChessBoard._meta.get_field("board"), [FieldTypes.STRING.value]),
    (Article._meta.get_field("publications"), [FieldTypes.INTEGER.value]),
))
def test_get_type(mapping):
    field, field_type = mapping
    assert get_type(field) == field_type
