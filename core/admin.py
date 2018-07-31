from django.contrib.gis import admin
from django.forms import modelform_factory, ALL_FIELDS
from simple_history.admin import SimpleHistoryAdmin


class ReasonedMixIn:
    def save_model(self, request, obj, form, change):
        # add `changeReason` for simple-history
        change_prefix = f'Admin: changed by {request.user}: '
        if not change:
            obj.changeReason = f'Admin: created by {request.user}: {repr(obj)}'
        elif form.changed_data:
            obj.changeReason = change_prefix + f'{repr(form.changed_data)}'
        else:
            obj.changeReason = change_prefix + 'save() without changes'
        if len(obj.changeReason) > 100:
            obj.changeReason = obj.changeReason[0:97] + '...'
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # add `changeReason` for simple-history
        obj.changeReason = f'Admin: deleted by {request.user}: {repr(obj)}'
        if len(obj.changeReason) > 100:
            obj.changeReason = obj.changeReason[0:97] + '...'
        super().delete_model(request, obj)


class PermittedFieldsMixIn:
    permitted_fields = dict()

    def _has_view_permission_only(self, request, obj):
        if obj is None:
            return not self.has_add_permission(request)

        return (self.has_view_permission(request, obj)
                and not self._has_change_only_permission(request, obj))

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
            if not self.has_field_permission(request, field)
        }
        return list(set(super().get_readonly_fields(request, obj)) | fields)

    def has_field_permission(self, request, field):
        if not self.permitted_fields:
            return False
        for permission, _fields in self.permitted_fields.items():
            meta = self.model._meta  # noqa: protected-access
            permission = permission.format(app_label=meta.app_label,
                                           model_name=meta.object_name)
            has_perm = (field in self.permitted_fields[permission]
                        and request.user.has_perm(permission))
            if has_perm:
                return True
        return False


class NonDeletableModelAdminMixIn:
    def has_delete_permission(self, request, obj=None):  # noqa: pylint=no-self-use
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class NonAddableModelAdminMixIn:
    def has_add_permission(self, request):  # noqa: pylint=no-self-use
        return False


class StrictMixIn(NonAddableModelAdminMixIn, NonDeletableModelAdminMixIn):
    pass


class SecuredModelAdmin(PermittedFieldsMixIn, ReasonedMixIn, admin.ModelAdmin):
    pass


class StrictSecuredModelAdmin(StrictMixIn, SecuredModelAdmin):
    pass


class SecuredAdminInline(PermittedFieldsMixIn, ReasonedMixIn,
                         admin.TabularInline):
    extra = 0


class StrictSecuredAdminInline(StrictMixIn, SecuredAdminInline):
    pass


class VersionedModelAdmin(SimpleHistoryAdmin):
    pass


class SecuredVersionedModelAdmin(VersionedModelAdmin, SecuredModelAdmin):
    pass


class StrictSecuredVersionedModelAdmin(StrictMixIn, VersionedModelAdmin,
                                       SecuredModelAdmin):
    pass


class RequiredInlineMixIn:
    validate_min = True
    extra = 0
    min_num = 1

    def get_formset(self, *args, **kwargs):  # noqa: pylint=arguments-differ
        return super().get_formset(validate_min=self.validate_min, *args,
                                   **kwargs)
