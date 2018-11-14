from unittest.mock import Mock

import pytest

from core.permitted_fields.admin import PermittedFieldsAdminMixIn

try:
    import admin_view_permission  # noqa unused-import
except ImportError:
    VIEW_PERMISSION = False
else:
    VIEW_PERMISSION = True


skip_admin_view_permission_missing = pytest.mark.skipif(  # noqa
    not VIEW_PERMISSION,
    reason='Django Admin View permission is missing')


@skip_admin_view_permission_missing
def test_obj_view_only():
    admin = PermittedFieldsAdminMixIn()
    admin.has_view_permission = Mock(return_value=True)
    admin.has_change_permission = Mock(return_value=False)  # noqa  protected-access

    assert admin._has_view_permission_only(request=Mock(), obj=Mock())  # noqa  protected-access


@skip_admin_view_permission_missing
def test_obj_view_and_change():
    admin = PermittedFieldsAdminMixIn()
    admin.has_view_permission = Mock(return_value=True)
    admin.has_change_permission = Mock(return_value=True)  # noqa  protected-access

    assert not admin._has_view_permission_only(request=Mock(), obj=Mock())  # noqa  protected-access


@skip_admin_view_permission_missing
def test_missing_obj_add_permission():
    admin = PermittedFieldsAdminMixIn()
    admin.has_add_permission = Mock(return_value=True)

    assert not admin._has_view_permission_only(request=Mock(), obj=None)  # noqa  protected-access


@skip_admin_view_permission_missing
def test_missing_obj_add_permission_missing(): # noqa: invalid-name
    admin = PermittedFieldsAdminMixIn()
    admin.has_add_permission = Mock(return_value=False)

    assert admin._has_view_permission_only(request=Mock(), obj=None)  # noqa  protected-access
