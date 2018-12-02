from django.contrib.gis import admin
from simple_history.admin import SimpleHistoryAdmin

from core.permitted_fields.admin import PermittedFieldsAdminMixIn


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


class SecuredModelAdmin(PermittedFieldsAdminMixIn, ReasonedMixIn,
                        admin.ModelAdmin):
    pass


class StrictSecuredModelAdmin(StrictMixIn, SecuredModelAdmin):
    pass


class SecuredAdminInline(PermittedFieldsAdminMixIn, ReasonedMixIn,
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
