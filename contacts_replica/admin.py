from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core.admin import StrictSecuredVersionedModelAdmin
from .models import ContactReplica


@admin.register(ContactReplica)
class ContactAdmin(StrictSecuredVersionedModelAdmin):
    list_display = ('name', 'phones', 'display_emails')
    search_fields = ('name', 'phones', 'emails')
    ordering = ['-id']

    def display_emails(self, obj):  # noqa: pylint=no-self-use
        return format_html_join(
            mark_safe('<br>'), '<a href="mailto:{0}">{0}</a>',
            [(x, ) for x in obj.emails])

    display_emails.short_description = _('e-mail')
    display_emails.allow_tags = True
