from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.gis import admin
from reversion.admin import VersionAdmin


class SecureAdminInline(admin.TabularInline):
    extra = 0

    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        self._validate_admin_protocol()
        opts = self.model._meta  # noqa: pylint: protected-access
        model_fields = [x.name for x in opts.get_fields()]
        fieldsets = flatten_fieldsets(self.get_fieldsets(request, obj))
        fields = set(model_fields) | set(self.readonly_fields) | set(fieldsets)
        return list(fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _validate_admin_protocol(self):
        class_dict = type(self).__dict__
        msg = "You should set `get_fieldsets` or `fieldsets` " \
              "to ModelAdmin ({})".format(type(self))
        assert 'get_fields' in class_dict or 'fields' in class_dict, msg


class SecureModelAdmin(admin.ModelAdmin):
    actions = None

    def get_actions(self, request):
        return None

    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        self._validate_admin_protocol()
        opts = self.model._meta  # noqa: pylint: protected-access
        model_fields = [x.name for x in opts.get_fields()]
        list_display = self.get_list_display(request)
        fieldsets = flatten_fieldsets(self.get_fieldsets(request, obj))
        fields = (set(model_fields) | set(self.readonly_fields) |
                  set(list_display) | set(fieldsets))
        return list(fields)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def _validate_admin_protocol(self):
        class_dict = type(self).__dict__
        msg = "You should set `get_fieldsets` or `fieldsets` " \
              "to ModelAdmin ({})".format(type(self))
        assert 'get_fieldsets' in class_dict or 'fieldsets' in class_dict, msg


class SecureVersionedModelAdmin(VersionAdmin, SecureModelAdmin):
    history_latest_first = True

    # disable restore deleted button
    change_list_template = "admin/change_list.html"
