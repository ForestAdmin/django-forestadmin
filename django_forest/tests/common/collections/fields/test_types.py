import pytest
from django_forest.common.collections.fields.types import (
    FieldTypes,
    RelationhipTypes,
    Field,
)
from django_forest.common.collections.fields.validations import (
    ValidationTypes,
    FieldValidationFactory,
)


@pytest.mark.parametrize(
    "name,expected",
    (
        ("STRING", "String"),
        ("INTEGER", "Integer"),
        ("BOOLEAN", "Boolean"),
        ("DATE", "DateOnly"),
        ("DATETIME", "Date"),
        ("FLOAT", "Float"),
        ("NUMBER", "Number"),
        ("JSON", "Json"),
        ("ENUM", "Enum"),
        ("TIME", "Time"),
        ("UNKNOWN", "unknown"),
    ),
)
def test_field_types(name, expected):
    assert FieldTypes[name].value == expected


@pytest.mark.parametrize(
    "name,expected",
    (
        ("HAS_MANY", "HasMany"),
        ("HAS_ONE", "HasOne"),
        ("BELONGS_TO", "BelongsTo"),
    ),
)
def test_relationship_types(name, expected):
    assert RelationhipTypes[name].value == expected


def test_base_field():
    field = Field(name="id", type=FieldTypes.STRING)
    assert field.is_related_field == False
    assert Field.serialize(field) == {
        "field": "id",
        "type": "String",
        "is_filterable": True,
        "is_sortable": True,
        "is_read_only": False,
        "is_required": False,
        "is_virtual": False,
        "default_value": None,
        "reference": None,
        "inverse_of": None,
        "relationship": None,
        "widget": None,
        "integration": None,
    }


def test_autocreated_field():
    field = Field(
        name="id",
        type=FieldTypes.INTEGER,
        is_autocreated=True,
        is_read_only=True,
    )
    assert field.is_related_field == False
    assert field.is_autocreated == True
    assert Field.serialize(field) == {
        "field": "id",
        "type": "Integer",
        "is_filterable": True,
        "is_sortable": True,
        "is_read_only": True,
        "is_required": False,
        "is_virtual": False,
        "default_value": None,
        "reference": None,
        "inverse_of": None,
        "relationship": None,
        "widget": None,
        "integration": None,
    }


def test_bad_autocreated_field():
    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            is_autocreated=True,
        )
    assert str(e.value) == "autocreated field should be read only"


def test_related_field():
    field = Field(
        name="id",
        type=FieldTypes.STRING,
        reference="reference",
        inverse_of="inverse_reference",
        relationship=RelationhipTypes.BELONGS_TO,
    )
    assert field.is_related_field == True
    assert Field.serialize(field) == {
        "field": "id",
        "type": "String",
        "is_filterable": True,
        "is_sortable": True,
        "is_read_only": False,
        "is_required": False,
        "is_virtual": False,
        "default_value": None,
        "reference": "reference",
        "inverse_of": "inverse_reference",
        "relationship": RelationhipTypes.BELONGS_TO.value,
        "widget": None,
        "integration": None,
    }


def test_bad_related_fields():
    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            reference="reference",
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            inverse_of="inverse_reference",
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            relationship=RelationhipTypes.BELONGS_TO,
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            relationship=RelationhipTypes.BELONGS_TO,
            reference="reference",
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            relationship=RelationhipTypes.BELONGS_TO,
            inverse_of="inverse_reference",
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.INTEGER,
            reference="reference",
            inverse_of="inverse_reference",
        )
    assert (
        str(e.value)
        == "inverse_of, reference and relationship are mandatory for the related fields"
    )


def test_bad_validation_field():
    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.STRING,
            is_read_only=True,
            validations=["Validator1"],
        )
    assert str(e.value) == "valdiations can't to be apply to related or read_only field"

    with pytest.raises(ValueError) as e:
        field = Field(
            name="id",
            type=FieldTypes.STRING,
            reference="reference",
            inverse_of="inverse_reference",
            relationship=RelationhipTypes.BELONGS_TO,
            validations=["Validator1"],
        )
    assert str(e.value) == "valdiations can't to be apply to related or read_only field"


def test_is_required_field():
    field = Field(
        name="id",
        type=FieldTypes.INTEGER,
        is_required=True,
    )
    assert field.is_related_field == False
    assert field.validations == [
        FieldValidationFactory.build(ValidationTypes.IS_PRESENT)
    ]
    assert Field.serialize(field,) == {
        "field": "id",
        "type": "Integer",
        "is_filterable": True,
        "is_sortable": True,
        "is_read_only": False,
        "is_required": True,
        "is_virtual": False,
        "default_value": None,
        "reference": None,
        "inverse_of": None,
        "relationship": None,
        "widget": None,
        "integration": None,
        "validations": [
            {
                "type": "is present",
                "message": "Ensure this value is not null or not empty",
            }
        ],
    }

    field = Field(
        name="id",
        type=FieldTypes.INTEGER,
        is_required=True,
        validations=[
            FieldValidationFactory.build(
                ValidationTypes.MAX_LENGTH,
                1,
            )
        ],
    )
    assert field.is_related_field == False
    assert field.validations == [
        FieldValidationFactory.build(
            ValidationTypes.MAX_LENGTH,
            1,
        ),
        FieldValidationFactory.build(ValidationTypes.IS_PRESENT),
    ]
    assert Field.serialize(field,) == {
        "field": "id",
        "type": "Integer",
        "is_filterable": True,
        "is_sortable": True,
        "is_read_only": False,
        "is_required": True,
        "is_virtual": False,
        "default_value": None,
        "reference": None,
        "inverse_of": None,
        "relationship": None,
        "widget": None,
        "integration": None,
        "validations": [
            {
                "type": "is shorter than",
                "message": "Ensure this value has at most 1 characters",
            },
            {
                "type": "is present",
                "message": "Ensure this value is not null or not empty",
            },
        ],
    }
