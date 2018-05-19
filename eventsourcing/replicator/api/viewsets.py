from rest_framework import serializers

from core.api.filters import StandardizedSearchFilter
from core.api.mixins import BulkCreateModelMixin
from core.api.serializers import StandardizedModelSerializer
from core.api.viewsets import StandardizedReadOnlyModelViewSet
from eventsourcing.replicator.registry import _get_replication_model
from eventsourcing.replicator.serializer import _check_serialize_problem, \
    SerializeHistoricalInstanceError
from ...consts import WEBHOOK_SUBSCRIPTION
from ...models import Subscription, subscribe


class _SubscriptionSerializer(StandardizedModelSerializer):
    type = serializers.ChoiceField(choices={1})

    def validate_name(self, value):
        q_set = Subscription.objects.filter(
            name=value, type=WEBHOOK_SUBSCRIPTION)
        if q_set.exists():
            subscription = q_set.last()
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

    def _check_webhook_url(self, value: str):
        if not isinstance(value, str) or not value:
            raise serializers.ValidationError(
                'settings.webhook_url has wrong format',
                code='settings_webhook_url_bad_format',
            )
        # TODO: add url validation

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
        self._check_webhook_url(webhook_url)

        version = int(self.context['view'].kwargs.get('version', 1))
        value.update({'api_version': version})
        return value

    def _check_event_name(self, event):
        splitted_event = event.split('.')
        _type = splitted_event[0]
        if not _get_replication_model(_type):
            raise serializers.ValidationError(
                'wrong event name',
                code='wrong_event',
            )
        if len(splitted_event) >= 2:
            _action = splitted_event[1]
            if _action not in ['+', '-', '~']:
                raise serializers.ValidationError(
                    'wrong event name',
                    code='wrong_event',
                )
        if len(splitted_event) > 3:
            raise serializers.ValidationError(
                'wrong event name',
                code='wrong_event',
            )

    def _check_event_permission(self, event):
        _type = event.split('.', 1)[0]
        model = _get_replication_model(_type)
        opts = model._meta  # noqa: pylint=protected-access
        codename = f'{opts.app_label}.view_{opts.model_name}'
        user = self.context['request'].user
        if not user.has_perm(codename):
            raise serializers.ValidationError(
                'no event permission',
                code='no_event_permission',
            )

    def _check_event_serilize_problem(self, user, settings, event):
        _type = event.split('.', 1)[0]
        try:
            _check_serialize_problem(user, settings, _type)
        except SerializeHistoricalInstanceError:
            raise serializers.ValidationError(
                f'serialize "{event}" event problem', code='serialize'
            )

    def validate_events(self, events):
        if not events:
            raise serializers.ValidationError(
                'no events',
                code='no_events',
            )
        events = serializers.ListField(child=serializers.CharField())\
            .to_internal_value(events)
        for event in events:
            self._check_event_name(event)
            self._check_event_permission(event)
        return events

    def validate(self, attrs):
        events = attrs['events']
        settings = attrs['settings']
        user = self.context['request'].user
        for event in events:
            self._check_event_serilize_problem(user, settings, event)
        return attrs

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
