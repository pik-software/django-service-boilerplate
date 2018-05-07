from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class ContactAdmin(admin.ModelAdmin):
    list_filter = ('type', 'events')
    list_display = ('name', 'user', 'events')
    search_fields = ('name', 'user', 'events')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)
