import pytest
from unittest.mock import Mock, patch
from django_forest.common.collections.fields.types import Field
from django_forest.common.collections.fields.factory import FieldFactory


def test_get_name():
    with pytest.raises(NotImplementedError):
        FieldFactory.get_name("")


def test_get_type():
    with pytest.raises(NotImplementedError):
        FieldFactory.get_type("")


def test_get_required():
    assert FieldFactory.get_required("") == False


def test_get_is_primary_key():
    assert FieldFactory.get_is_primary_key("") == False


def test_get_is_autocreated():
    assert FieldFactory.get_is_autocreated("") == False


def test_get_is_read_only():
    with patch(
        "django_forest.common.collections.fields.factory.FieldFactory.get_is_autocreated",
        return_value=False,
    ) as m:
        assert FieldFactory.get_is_read_only("") == False
        m.assert_called_once_with("")

    with patch(
        "django_forest.common.collections.fields.factory.FieldFactory.get_is_autocreated",
        return_value=True,
    ) as m:
        assert FieldFactory.get_is_read_only("") == True
        m.assert_called_once_with("")


def test_get_is_filterable():
    assert FieldFactory.get_is_filterable("") == True


def test_is_sortable():
    assert FieldFactory.get_is_sortable("") == True


def test_get_default_value():
    assert FieldFactory.get_default_value("") == None


def test_get_enum_values():
    assert FieldFactory.get_enum_values("") == None


def test_get_reference():
    assert FieldFactory.get_reference("") == None


def test_get_relationship():
    assert FieldFactory.get_relationship("") == None


def test_get_inverse_of():
    assert FieldFactory.get_inverse_of("") == None


def test_get_validations():
    assert FieldFactory.get_validations("") == []


@patch.object(FieldFactory, "get_name", return_value="name")
@patch.object(FieldFactory, "get_type", return_value="type")
@patch.object(FieldFactory, "get_is_autocreated", return_value="autocreated")
@patch.object(FieldFactory, "get_required", return_value="required")
@patch.object(FieldFactory, "get_is_read_only", return_value="read_only")
@patch.object(FieldFactory, "get_is_primary_key", return_value="is_pk")
@patch.object(FieldFactory, "get_is_sortable", return_value="sortable")
@patch.object(FieldFactory, "get_is_filterable", return_value="filterable")
@patch.object(FieldFactory, "get_relationship", return_value="relationship")
@patch.object(FieldFactory, "get_inverse_of", return_value="inverse_of")
@patch.object(FieldFactory, "get_reference", return_value="reference")
@patch.object(FieldFactory, "get_default_value", return_value="default_value")
@patch.object(FieldFactory, "get_enum_values", return_value="enum")
@patch.object(FieldFactory, "get_validations", return_value="validations")
@patch("django_forest.common.collections.fields.factory.Field")
def test_build(MockedField, *mocked_fn):
    with patch.object(FieldFactory, "has_many_values", return_value=False):
        _Field = Mock(spec=Field("", ""))
        MockedField.return_value = _Field

        res = FieldFactory.build("field")

        for fn in mocked_fn:
            fn.assert_called_once_with("field")
        MockedField.assert_called_once_with(
            name="name",
            type="type",
            is_autocreated="autocreated",
            is_required="required",
            is_read_only="read_only",
            is_primary_key="is_pk",
            is_sortable="sortable",
            is_filterable="filterable",
            relationship="relationship",
            inverse_of="inverse_of",
            reference="reference",
            default_value="default_value",
            enums="enum",
            validations="validations",
        )
        assert res == _Field
        assert isinstance(res.type, list) is False

    for fn in mocked_fn:
        fn.reset_mock()
        MockedField.reset_mock()

    with patch.object(FieldFactory, "has_many_values", return_value=True):
        _Field = Mock(spec=Field("", ""))
        MockedField.return_value = _Field

        res = FieldFactory.build("field")

        for fn in mocked_fn:
            fn.assert_called_once_with("field")
        MockedField.assert_called_once_with(
            name="name",
            type="type",
            is_autocreated="autocreated",
            is_required="required",
            is_read_only="read_only",
            is_primary_key="is_pk",
            is_sortable="sortable",
            is_filterable="filterable",
            relationship="relationship",
            inverse_of="inverse_of",
            reference="reference",
            default_value="default_value",
            enums="enum",
            validations="validations",
        )
        assert res == _Field
        assert isinstance(res.type, list)
