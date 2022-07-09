from django_forest.common.collections.fields.validations import ValidationTypes
import pytest
from unittest.mock import call, patch
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_forest.tests.models import (
    Article,
    Publication,
    Question,
    Restaurant,
    Waiter,
    Student,
    ChessBoard,
    Place,
    Topic,
)

from django_forest.collections.fields.factory import DjangoFieldFactory
from django_forest.common.collections.fields.types import FieldTypes, RelationhipTypes


@pytest.mark.parametrize(
    "field,expected",
    (
        (Article._meta.get_field("headline"), "headline"),
        (Article._meta.get_field("publications"), "publications"),
        (Publication._meta.get_field("article"), "article_set"),
    ),
)
def test_get_name(field, expected):
    assert DjangoFieldFactory.get_name(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (Student._meta.get_field("year_in_school"), True),
        (Student._meta.get_field("id"), False),
    ),
)
def test_is_enum(field, expected):
    assert DjangoFieldFactory._is_enum(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (Student._meta.get_field("year_in_school"), FieldTypes.STRING),
        (Restaurant._meta.get_field("serves_hot_dogs"), FieldTypes.BOOLEAN),
        (Waiter._meta.get_field("restaurant"), FieldTypes.UNKNOWN),
    ),
)
def test_map_django_type(field, expected):
    with patch.dict(
        "django_forest.collections.fields.factory.FIELD_TYPES_MAPPING",
        {
            models.CharField: FieldTypes.STRING,
            models.BooleanField: FieldTypes.BOOLEAN,
        },
    ):
        assert DjangoFieldFactory.map_django_type(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (Student._meta.get_field("year_in_school"), False),
        (Restaurant._meta.get_field("serves_hot_dogs"), False),
        (ChessBoard._meta.get_field("board"), True),
    ),
)
def test_has_many_values(field, expected):
    with patch(
        "django_forest.collections.fields.factory.FieldFactory.has_many_values",
        return_value=False,
    ):
        assert DjangoFieldFactory.has_many_values("", field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (Waiter._meta.get_field("restaurant"), RelationhipTypes.BELONGS_TO),
        (Restaurant._meta.get_field("place"), RelationhipTypes.HAS_ONE),
        (Article._meta.get_field("publications"), RelationhipTypes.HAS_MANY),
        (Restaurant._meta.get_field("waiter"), RelationhipTypes.HAS_MANY),
    ),
)
def test_get_relationship(field, expected):
    assert DjangoFieldFactory.get_relationship(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (Place._meta.get_field("restaurant"), FieldTypes.INTEGER),
        (Restaurant._meta.get_field("place"), FieldTypes.INTEGER),
        (Article._meta.get_field("publications"), FieldTypes.INTEGER),
    ),
)
def test_get_related_type(field, expected):
    with patch.dict(
        "django_forest.collections.fields.factory.FIELD_TYPES_MAPPING",
        {
            models.AutoField: FieldTypes.INTEGER,
        },
    ):
        assert DjangoFieldFactory.get_related_type(field) == expected


@patch.object(DjangoFieldFactory, "get_related_type", return_value="RelatedType")
@patch.object(DjangoFieldFactory, "map_django_type", return_value="MapDjangoType")
def test_get_type(mock_map_django_type, mock_get_related_type):

    field = Article._meta.get_field("publications")
    res = DjangoFieldFactory.get_type(field)
    assert res == "RelatedType"
    mock_get_related_type.assert_called_once_with(field)

    mock_get_related_type.reset_mock()

    field = ChessBoard._meta.get_field("board")
    res = DjangoFieldFactory.get_type(field)
    assert res == "MapDjangoType"
    mock_map_django_type.assert_called_once_with(field.base_field)
    mock_map_django_type.reset_mock()

    field = Student._meta.get_field("year_in_school")
    res = DjangoFieldFactory.get_type(field)
    assert res == FieldTypes.ENUM

    field = Student._meta.get_field("id")
    res = DjangoFieldFactory.get_type(field)
    assert res == "MapDjangoType"
    mock_map_django_type.assert_called_once_with(field)


@pytest.mark.parametrize(
    "field,expected",
    (
        (models.IntegerField(), None),
        (models.IntegerField(default=1), "1"),
        (models.IntegerField(default=models.NOT_PROVIDED), None),
    ),
)
def test_get_default_value(field, expected):
    assert DjangoFieldFactory.get_default_value(field) == expected


@pytest.mark.parametrize(
    "field,default_value,expected",
    (
        (models.IntegerField(null=False), None, True),
        (models.IntegerField(blank=False), None, True),
        (models.IntegerField(null=False, blank=False), None, True),
        (models.IntegerField(null=False), 1, False),
        (models.IntegerField(blank=False), 2, False),
        (models.IntegerField(null=False, blank=False), 3, False),
        (models.IntegerField(null=False, blank=True), 3, False),
        (models.IntegerField(null=True, blank=False), 3, False),
        (models.IntegerField(null=True, blank=True), None, False),
        (models.IntegerField(null=True, blank=False), None, False),
        (models.IntegerField(null=False, blank=True), None, False),
        (models.IntegerField(null=True), None, False),
        (models.IntegerField(blank=True), None, False),
    ),
)
def test_get_required(field, default_value, expected):
    with patch.object(
        DjangoFieldFactory, "get_default_value", return_value=default_value
    ):
        assert DjangoFieldFactory.get_required(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (models.IntegerField(), False),
        (models.IntegerField(primary_key=True), True),
        (models.IntegerField(primary_key=False), False),
    ),
)
def test_get_is_primary_key(field, expected):
    assert DjangoFieldFactory.get_is_primary_key(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (models.IntegerField(), False),
        (Waiter._meta.get_field("id"), True),
    ),
)
def test_get_is_autocreated(field, expected):
    assert DjangoFieldFactory.get_is_autocreated(field) == expected


@pytest.mark.parametrize(
    "field,super_read_only,expected",
    (
        (models.IntegerField(), False, False),
        (models.IntegerField(), True, True),
        (models.IntegerField(editable=True), False, False),
        (models.IntegerField(editable=True), True, True),
        (models.IntegerField(editable=False), False, True),
        (models.IntegerField(editable=False), True, True),
    ),
)
def test_get_is_read_only(field, super_read_only, expected):
    with patch(
        "django_forest.collections.fields.factory.FieldFactory.get_is_read_only",
        return_value=super_read_only,
    ):
        assert DjangoFieldFactory.get_is_read_only(field) == expected


@pytest.mark.parametrize(
    "field,is_enum,expected",
    (
        (models.IntegerField(), False, None),
        (models.CharField(choices=((0, 1), (2, 3), (4, 5))), True, ["0", "2", "4"]),
        (
            models.CharField(blank=True, choices=((0, 1), (2, 3), (4, 5))),
            True,
            ["", "0", "2", "4"],
        ),
    ),
)
def test_get_enum_values(field, is_enum, expected):
    with patch.object(DjangoFieldFactory, "_is_enum", return_value=is_enum):
        assert DjangoFieldFactory.get_enum_values(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (models.IntegerField(), None),
        (Article._meta.get_field("publications"), "tests_publication.id"),
        (Publication._meta.get_field("article"), "tests_article.id"),
        (Question._meta.get_field("topic"), "tests_topic.id"),
        (Topic._meta.get_field("question"), "tests_question.id"),
        (Restaurant._meta.get_field("place"), "tests_place.id"),
        (Place._meta.get_field("restaurant"), "tests_restaurant.place_id"),
    ),
)
def test_get_reference(field, expected):
    assert DjangoFieldFactory.get_reference(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (models.IntegerField(), None),
        (Article._meta.get_field("publications"), "article_set"),
        (Publication._meta.get_field("article"), "publications"),
        (Question._meta.get_field("topic"), "question_set"),
        (Topic._meta.get_field("question"), "topic"),
        (Restaurant._meta.get_field("place"), "restaurant"),
        (Place._meta.get_field("restaurant"), "place"),
    ),
)
def test_get_inverse_of(field, expected):
    assert DjangoFieldFactory.get_inverse_of(field) == expected


@pytest.mark.parametrize(
    "field,super_is_filterable,expected",
    (
        (models.IntegerField(), False, False),
        (models.IntegerField(), True, True),
        (Article._meta.get_field("publications"), False, False),
        (Publication._meta.get_field("article"), True, False),
        (Question._meta.get_field("topic"), False, False),
        (Question._meta.get_field("topic"), True, True),
        (Topic._meta.get_field("question"), False, False),
        (Topic._meta.get_field("question"), True, False),
    ),
)
def test_get_is_filterable(field, super_is_filterable, expected):
    with patch(
        "django_forest.collections.fields.factory.FieldFactory.get_is_filterable",
        return_value=super_is_filterable,
    ):
        assert DjangoFieldFactory.get_is_filterable(field) == expected


@pytest.mark.parametrize(
    "field,expected",
    (
        (
            models.IntegerField(
                validators=[MaxValueValidator(2), MinValueValidator(1)]
            ),
            ((ValidationTypes.MAX_VALUE, 2), (ValidationTypes.MIN_VALUE, 1)),
        ),
        (models.CharField(max_length=2), ((ValidationTypes.MAX_LENGTH, 2),)),
        (models.FloatField(), []),
    ),
)
def test_get_validations(field, expected):
    with patch(
        "django_forest.collections.fields.factory.FieldValidationFactory.build"
    ) as m:
        m.return_value = "mocked"
        res = DjangoFieldFactory.get_validations(field)
        if expected:
            m.assert_has_calls([call(*args) for args in expected])
            assert res == ["mocked" for _ in expected]
        else:
            assert res == []
