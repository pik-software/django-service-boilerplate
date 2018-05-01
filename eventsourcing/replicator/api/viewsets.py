from rest_framework import serializers

from core.api.filters import StandardizedSearchFilter
from core.api.mixins import BulkCreateModelMixin
from core.api.serializers import StandardizedModelSerializer
from core.api.viewsets import StandardizedReadOnlyModelViewSet
from eventsourcing.replicator.registry import _is_replicating_type, \
    _get_replication_model
from ...consts import WEBHOOK_SUBSCRIPTION
from ...models import Subscription, subscribe


class _SubscriptionSerializer(StandardizedModelSerializer):
    type = serializers.ChoiceField(choices={1})

    def validate_name(self, value):
        qs = Subscription.objects.filter(name=value, type=WEBHOOK_SUBSCRIPTION)
        if qs.exists():
            subscription = qs.last()
            if subscription.user != self.context['request'].user:
                raise serializers.ValidationError(
                    'Name is already used by another user',
                    code='name_used_by_another_user')
        return value

    def _check_webhook_headers(self, value):
        try:
            return serializers.DictField(child=serializers.CharField())\
                .to_internal_value(value)
        except serializers.ValidationError:
            raise serializers.ValidationError(
                'settings.webhook_headers has wrong format',
                code='settings_webhook_headers_bad_format',
            )

    def _check_webhook_auth(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise serializers.ValidationError(
                'settings.webhook_auth has wrong format',
                code='settings_webhook_auth_bad_format',
            )

    def validate_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                'settings is not a dictionary',
                code='settings_wrong_type')
        if 'webhook_url' not in value:
            raise serializers.ValidationError(
                'settings.webhook_url not exists',
                code='no_webhook_url')

        if 'webhook_headers' in value:
            webhook_headers = value['webhook_headers']
            self._check_webhook_headers(webhook_headers)

        if 'webhook_auth' in value:
            webhook_auth = value['webhook_auth']
            self._check_webhook_auth(webhook_auth)

        webhook_url = value['webhook_url']
        # TODO: validate url

        version = int(self.context['view'].kwargs.get('version', 1))
        value.update({'api_version': version})
        return value

    def validate_events(self, events):
        if not events:
            raise serializers.ValidationError(
                'no events',
                code='no_events',
            )
        events = serializers.ListField(child=serializers.CharField())\
            .to_internal_value(events)
        for event in events:
            event = event.split('.', 1)[0]
            model = _get_replication_model(event)
            if not model:
                raise serializers.ValidationError(
                    'wrong event name',
                    code='wrong_event',
                )
            codename = f'{model._meta.app_label}.view_historical' \
                       f'{model._meta.model_name}'
            user = self.context['request'].user
            if not user.has_perm(codename):
                raise serializers.ValidationError(
                    'no event permission',
                    code='no_event_permission',
                )

        return events

    def create(self, validated_data):
        name = validated_data['name']
        settings = validated_data['settings']
        events = validated_data['events']
        type_ = validated_data['type']
        return subscribe(
            self.context['request'].user,
            name, type_, settings, events)

    def update(self, instance, validated_data):
        return self.create(validated_data)

    class Meta:
        model = Subscription
        read_only_fields = (
            '_uid', '_type',
        )
        fields = (
            '_uid', '_type', 'name', 'type', 'settings', 'events',
        )


class SubscriptionViewSet(
    BulkCreateModelMixin, StandardizedReadOnlyModelViewSet
):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = _SubscriptionSerializer
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedSearchFilter, )
    search_fields = (
        'name', )

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
