from django.utils.translation import ugettext_lazy as _
from rest_framework import status, serializers
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from core.api.viewsets import StandardizedGenericViewSet
from ..processor import _process_historical_record, \
    _ProcessHistoricalRecordError
from ...consts import ACTIONS


class _WebhookProcessingError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('WebhookCallbackViewSet processing error')
    default_code = "webhook_processing_error"


class _HistoryListItemSerializer(serializers.Serializer):
    _type = serializers.CharField()
    _uid = serializers.CharField()
    _version = serializers.IntegerField()
    history_type = serializers.ChoiceField(choices=ACTIONS)
    history_date = serializers.DateTimeField()


class _HistoryListItem(serializers.DictField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        _HistoryListItemSerializer(data=data).is_valid(raise_exception=True)
        return data


class _HistorySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = serializers.ListField(child=_HistoryListItem())


class WebhookCallbackViewSet(StandardizedGenericViewSet):
    serializer_class = _HistorySerializer

    def list(self, request, *args, **kwargs):
        return Response({"status": "ok"})

    def create(self, request, *args, **kwargs):
        # TODO: check permission!?

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        objects = serializer.data['results']
        for obj in objects:
            _type, _uid, _version = obj['_type'], obj['_uid'], obj['_version']
            _action = obj['history_type']
            try:
                _process_historical_record(_type, _action, _uid, _version, obj)
            except _ProcessHistoricalRecordError as exc:
                raise _WebhookProcessingError(f"WEBHOOK: {exc}")

        return Response({"status": "ok"})
