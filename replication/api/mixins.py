from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.api.mixins import HistoryViewSetMixin
from core.api.serializers import StandardizedModelSerializer
from replication.consts import WEBHOOK_SUBSCRIPTION
from replication.models import Subscribe, create_or_update_subscription


class SubscribeSerializer(StandardizedModelSerializer):
    def validate_type(self, value):
        if value != 1:
            raise serializers.ValidationError("Only WEBHOOK is available")
        return value

    def validate_name(self, value):
        qs = Subscribe.objects.filter(name=value, type=WEBHOOK_SUBSCRIPTION)
        if qs.exists():
            subscription = qs.last()
            if subscription.user != self.context['request'].user:
                raise serializers.ValidationError(
                    'Name is already used by another user',
                    code='name_used_by_another_user')
        return value

    def validate_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                'settings is not a dictionary',
                code='settings_wrong_type')
        if 'webhook_url' not in value:
            raise serializers.ValidationError(
                'settings.webhook_url not exists',
                code='no_webhook_url')

        webhook_url = value['webhook_url']
        # TODO: validate url
        return value

    def create(self, validated_data):
        name = validated_data['name']
        settings = validated_data['settings']
        events = validated_data['events']
        return create_or_update_subscription(
            self.context['request'].user,
            name, WEBHOOK_SUBSCRIPTION, settings, events)

    class Meta:
        model = Subscribe
        read_only_fields = (
            '_uid', '_type', 'events', 'type',
        )
        fields = (
            '_uid', '_type', 'events', 'type', 'name', 'settings',
        )


class SubscribeViewSetMixin(HistoryViewSetMixin):
    allow_subscribe = False

    def get_event_serializer(self, *args, **kwargs):
        return self.get_history_serializer(*args, **kwargs)

    def get_subscribe_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return SubscribeSerializer(*args, **kwargs)

    def has_subscribe_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        return True
        # TODO (pahaz): Use this as default permission check for all APIs
        opts = self.get_queryset().model._meta  # noqa: pylint=protected-access
        method = request.method.lower()
        codename = f'can_{method}_api_{opts.model_name}_{self.action}'
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    @action(methods=['POST'], detail=False)
    def subscribe(self, request, **kwargs):
        version = int(kwargs.get('version'))
        if not self.allow_subscribe:
            self.permission_denied(
                request,
                message='You do not have permission to subscribe on objects'
            )

        if not self.has_subscribe_permission(request):
            self.permission_denied(
                request, message='Access denied'
            )

        opts = self.get_queryset().model._meta
        model_name = opts.model_name
        serializer = self.get_subscribe_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['settings'].update({'api_version': version})
        serializer.save(
            events=[
                f'{model_name}',
                # f'{model_name}.+', f'{model_name}.-', f'{model_name}.~',
            ],
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK)
