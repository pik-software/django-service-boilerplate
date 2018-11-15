from unittest.mock import Mock

from core.permitted_fields.admin import PermittedFieldsAdminMixIn


def test_obj_view_only():
    admin = PermittedFieldsAdminMixIn()
    admin.has_view_permission = Mock(return_value=True)
    admin.has_change_permission = Mock(return_value=False)  # noqa  protected-access

    assert admin._has_view_permission_only(request=Mock(), obj=Mock())  # noqa  protected-access


def test_obj_view_and_change():
    admin = PermittedFieldsAdminMixIn()
    admin.has_view_permission = Mock(return_value=True)
    admin.has_change_permission = Mock(return_value=True)  # noqa  protected-access

    assert not admin._has_view_permission_only(request=Mock(), obj=Mock())  # noqa  protected-access


def test_missing_obj_add_permission():
    admin = PermittedFieldsAdminMixIn()
    admin.has_add_permission = Mock(return_value=True)

    assert not admin._has_view_permission_only(request=Mock(), obj=None)  # noqa  protected-access


def test_missing_obj_add_permission_missing(): # noqa: invalid-name
    admin = PermittedFieldsAdminMixIn()
    admin.has_add_permission = Mock(return_value=False)

    assert admin._has_view_permission_only(request=Mock(), obj=None)  # noqa  protected-access
