from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from core.admin import SecuredVersionedModelAdmin, SecuredAdminInline
from .models import Contact, Comment


class SetUserMixin:
    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'user_id') and not obj.user_id:
            obj.user_id = request.user.pk
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            instances = formset.save(commit=False)
            for instance in instances:
                if hasattr(instance, 'user_id') and not instance.user_id:
                    instance.user_id = request.user.pk
        super().save_related(request, form, formsets, change)


class CommentInline(SecuredAdminInline):
    model = Comment

    permitted_fields = {
        'contacts.change_comment': ('message', )
    }


@admin.register(Contact)
class ContactAdmin(SetUserMixin, SecuredVersionedModelAdmin):
    list_display = ('name', 'phones', 'display_emails')
    search_fields = ('name', 'phones', 'emails')
    ordering = ('order_index', '-id')

    fieldsets = ((
        None,
        {'fields': ('name', 'phones', 'emails', 'order_index')}),
    )

    inlines = (CommentInline, )

    permitted_fields = {
        'contacts.change_contact': ('name', 'phones', 'emails', 'order_index')
    }

    def display_emails(self, obj):  # noqa: pylint=no-self-use
        return format_html_join(
            mark_safe('<br>'), '<a href="mailto:{0}">{0}</a>',
            [(x, ) for x in obj.emails])

    display_emails.short_description = _('e-mail')
    display_emails.allow_tags = True
