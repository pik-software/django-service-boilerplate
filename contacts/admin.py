from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core.admin import SecuredVersionedModelAdmin, SecuredAdminInline, \
    AutoSetRequestUserMixIn
from .models import Contact, Comment


class CommentInline(SecuredAdminInline):
    model = Comment


@admin.register(Contact)
class ContactAdmin(AutoSetRequestUserMixIn, SecuredVersionedModelAdmin):
    list_display = ('name', 'phones', 'display_emails')
    search_fields = ('name', 'phones', 'emails')
    ordering = ('order_index', '-id')

    fieldsets = ((
        None,
        {'fields': (
            'name', 'phones', 'emails', 'order_index'
        )}),
    )

    inlines = (CommentInline,)

    def display_emails(self, obj):  # noqa: pylint=no-self-use
        return format_html_join(
            mark_safe('<br>'), '<a href="mailto:{0}">{0}</a>',
            [(x, ) for x in obj.emails])

    display_emails.short_description = _('e-mail')
    display_emails.allow_tags = True
