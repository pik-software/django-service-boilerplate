from collections import OrderedDict

import rest_framework_filters as filters
from django.db.models import DateTimeField
from django.urls import NoReverseMatch
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer

from core.api.filters import StandardizedFieldFilters, \
    StandardizedOrderingFilter, StandardizedSearchFilter
from core.api.viewsets import StandardizedModelViewSet
from .models import EntityType, Entity
from .utils.swagger import convert_data_to_schema, validate_data_by_schema


class EntitySerializer(Serializer):
    def create(self, validated_data):
        return Entity.objects.create(
            type=self.context['type'],
            value=validated_data)

    def is_valid(self, raise_exception=False):
        return super().is_valid(raise_exception)

    def update(self, instance, validated_data):
        instance.value.update(validated_data)
        instance.save()
        return instance

    def _get_schema(self):
        schema = self.context.get('schema')
        _type = self.context.get('type')
        if not schema and _type:
            return _type.schema
        return schema

    def to_internal_value(self, data):
        schema = self._get_schema()
        if not schema:
            return OrderedDict(data)
        ret, errors = validate_data_by_schema(
            data, schema, partial=self.partial)
        if errors:
            raise ValidationError(errors)
        return ret

    def to_representation(self, instance: Entity):
        schema = self._get_schema()
        data = {
            '_uid': instance.pk,
            '_type': instance.type.slug,
            '_version': instance.version,
            'created': instance.created,
            'updated': instance.updated,
        }
        data.update(instance.value)
        if schema:
            data = convert_data_to_schema(data, schema)
        return data


class EntityFilter(filters.FilterSet):
    class Meta:
        model = Entity
        fields = {
            'updated': ['exact', 'gt', 'gte', 'lt', 'lte'],
            'created': ['exact', 'gt', 'gte', 'lt', 'lte'],
        }
        filter_overrides = {
            DateTimeField: {'filter_class': filters.IsoDateTimeFilter}
        }


class APIEntityViewSet(StandardizedModelViewSet):
    lookup_field = 'uid'
    lookup_url_kwarg = '_uid'
    ordering = '-created'
    serializer_class = EntitySerializer
    allow_bulk_create = True
    allow_history = True

    filter_backends = (
        StandardizedFieldFilters, StandardizedSearchFilter,
        StandardizedOrderingFilter)
    filter_class = EntityFilter
    search_fields = ('value',)
    ordering_fields = ('created', 'updated')

    entity_type = None  # for introspection
    schema = None  # exclude from schema

    def dispatch(self, request, *args, **kwargs):
        _type = kwargs['_type']
        self.entity_type = get_object_or_404(EntityType, slug=_type)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['type'] = self.entity_type
        return ctx

    def get_queryset(self):
        return Entity.objects.filter(type=self.entity_type)


class APIRootView(views.APIView):
    _ignore_model_permissions = True
    schema = None  # exclude from schema
    api_root_dict = None

    def get(self, request, *args, **kwargs):
        ret = OrderedDict()
        namespace = request.resolver_match.namespace
        for key, url_name in self.api_root_dict.items():
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    args=args,
                    kwargs=kwargs,
                    request=request,
                    format=kwargs.get('format', None)
                )
            except NoReverseMatch:
                continue

        for entity in EntityType.objects.all():
            url_name = namespace + ':entity-list' if namespace else 'entity-list'
            kwargs['_type'] = entity.slug
            ret[entity.slug + '-list'] = reverse(
                url_name,
                args=args,
                kwargs=kwargs,
                request=request,
                format=kwargs.get('format', None)
            )
        return Response(ret)
