from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core.admin import SecureVersionedModelAdmin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(SecureVersionedModelAdmin):
    list_display = ('name', 'phones', 'display_emails')
    search_fields = ('name', 'phones', 'emails')
    ordering = ['order_index', '-id']

    fieldsets = ((
        None,
        {'fields': (
            'name', 'phones', 'emails', 'order_index'
        )}),
    )

    def display_emails(self, obj):  # noqa: pylint: no-self-use
        return format_html_join(
            mark_safe('<br>'), '<a href="mailto:{0}">{0}</a>',
            [(x, ) for x in obj.emails])

    display_emails.short_description = _('e-mail')
    display_emails.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        if request.user.has_perm('contacts.can_edit_contact'):
            fields.remove('name')
            fields.remove('phones')
            fields.remove('emails')
            fields.remove('order_index')
        return fields

    def has_add_permission(self, request):
        return super(admin.ModelAdmin, self).has_add_permission(request)  # noqa: pylint: bad-super-call

    def has_change_permission(self, request, obj=None):
        return super(admin.ModelAdmin, self).has_change_permission(request, obj)  # noqa: pylint: bad-super-call

    def has_delete_permission(self, request, obj=None):
        return super(admin.ModelAdmin, self).has_delete_permission(request, obj)  # noqa: pylint: bad-super-call
