from django.forms import ALL_FIELDS, modelform_factory

from .permitted import PermittedFieldsPermissionMixIn


class PermittedFieldsAdminMixIn(PermittedFieldsPermissionMixIn):
    def _has_view_permission_only(self, request, obj):
        if obj is None:
            return not self.has_add_permission(request)

        return (self.has_view_permission(request, obj)
                and not self.has_change_permission(request, obj))

    def get_model_fields(self, obj):
        form_class = modelform_factory(self.model, self.form, ALL_FIELDS)
        form = form_class(instance=obj)
        return form.fields.keys()

    def get_readonly_fields(self, request, obj=None):
        if self._has_view_permission_only(request, obj):
            return super().get_readonly_fields(request, obj)

        fields = {
            field
            for field in self.get_model_fields(obj)
            if not self.has_field_permission(request.user, self.model, field)
        }
        original = set(super().get_readonly_fields(request, obj))
        return list(original | fields)
