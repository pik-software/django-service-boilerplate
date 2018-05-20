from django.contrib import admin

from .replicator.registry import _get_all_replication_models, re_replicate
from .models import Subscription


def _make_send_events_action(name, model):
    def _send_history(modeladmin, request, subscriptions):
        for subscription in subscriptions:
            re_replicate(subscription, [name])
    return _send_history, f'send_{name}_events', f"Send all {name} events"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_filter = ('type', 'events')
    list_display = ('name', 'user', 'events')
    search_fields = ('name', 'user', 'events')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        actions = super().get_actions(request)
        for name, model in _get_all_replication_models():
            actions[f'send_{name}_events'] = _make_send_events_action(
                name, model)
        return actions
