from unittest import mock

import pytest

from ..permitted import PermittedFieldsPermissionMixIn


@pytest.fixture
def model():
    return mock.Mock(
        permitted_fields={'{app_label}_can_change_{model_name}': ['a']},
        _meta=mock.Mock(
            app_label='MockApp',
            object_name='MockModel'
        )
    )


def test_perm_format(model):
    user = mock.Mock()
    PermittedFieldsPermissionMixIn().has_field_permission(
        user=user, model=model, field='a')
    calls = [mock.call('mockapp_can_change_mockmodel')]
    assert user.has_perm.mock_calls == calls


def test_got_field_and_perm(model):
    user_with_perm = mock.Mock(has_perm=mock.Mock(return_value=True))

    a_is_editable = PermittedFieldsPermissionMixIn().has_field_permission(
        user=user_with_perm, model=model, field='a')
    assert a_is_editable


def test_missing_field(model):
    user_with_perm = mock.Mock(has_perm=mock.Mock(return_value=True))

    b_is_editable = PermittedFieldsPermissionMixIn().has_field_permission(
        user=user_with_perm, model=model, field='b')
    assert not b_is_editable


def test_missing_perm(model):
    user_without_perm = mock.Mock(has_perm=mock.Mock(return_value=False))
    a_is_editable = PermittedFieldsPermissionMixIn().has_field_permission(
        user=user_without_perm, model=model, field='a')
    assert not a_is_editable


def test_missing_perm_and_field(model):
    user_without_perm = mock.Mock(has_perm=mock.Mock(return_value=False))
    a_is_editable = PermittedFieldsPermissionMixIn().has_field_permission(
        user=user_without_perm, model=model, field='b')
    assert not a_is_editable
