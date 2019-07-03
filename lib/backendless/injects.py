from django.urls import path
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings

from .api import APIEntityViewSet, APIRootView
from .models import EntityType
from .utils.funcs import post_process_by


def _make_paginated_schema(entity):
    return openapi.Schema(**{
        'properties': {
            'count': {'type': 'integer'},
            'page': {'type': 'integer'},
            'page_next': {'type': 'integer', 'x-nullable': True},
            'page_previous': {'type': 'integer', 'x-nullable': True},
            'page_size': {'type': 'integer'},
            'pages': {'type': 'integer'},
            'results': {
                'items': {'$ref': f'#/definitions/{entity}'},
                'type': 'array'}},
        'required': ['results', 'count', 'page', 'page_size'],
        'type': 'object'})


def _make_ref_schema(entity):
    return {'$ref': f'#/definitions/{entity}'}


def _body_params(entity):
    return [openapi.Parameter(**{
        'in_': 'body',
        'name': 'data',
        'required': True,
        'schema': {'$ref': f'#/definitions/{entity}'}})]


def _query_params(entity):
    return [openapi.Parameter(**x) for x in [
        {'description': '',
         'in_': 'query',
         'name': 'updated',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'updated__gt',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'updated__gte',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'updated__lt',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'updated__lte',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'created',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'created__gt',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'created__gte',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'created__lt',
         'required': False,
         'type': 'string'},
        {'description': '',
         'in_': 'query',
         'name': 'created__lte',
         'required': False,
         'type': 'string'},
        {'description': 'A search term.',
         'in_': 'query',
         'name': 'search',
         'required': False,
         'type': 'string'},
        {'description': 'Which field to use when ordering the results.',
         'in_': 'query',
         'name': 'ordering',
         'required': False,
         'type': 'string'},
        {'description': 'A page number within the paginated result set.',
         'in_': 'query',
         'name': 'page',
         'required': False,
         'type': 'integer'},
        {'description': 'Number of results to return per page.',
         'in_': 'query',
         'name': 'page_size',
         'required': False,
         'type': 'integer'}]]


def _add_backendless_urls(urls):
    return urls + [
        path('<str:_type>-list/<str:_uid>/',
             APIEntityViewSet.as_view({
                 'get': 'retrieve',
                 'put': 'update',
                 'patch': 'partial_update',
                 'delete': 'destroy'
             }),
             name='entity-detail'),
        path('<str:_type>-list/',
             APIEntityViewSet.as_view({
                 'get': 'list',
                 'post': 'create'
             }),
             name='entity-list'),
    ]


def _add_schema(swagger: openapi.Swagger):
    for entity in EntityType.objects.all():
        name = f'{entity.slug}-list'
        swagger.definitions[entity.slug] = openapi.Schema(**entity.schema)
        swagger.paths[f'/{name}/'] = openapi.PathItem(
            get=openapi.Operation(
                operation_id=f'{name}_list',
                responses=openapi.Responses({
                    '200': openapi.Response(
                        description='',
                        schema=_make_paginated_schema(entity.slug))}),
                tags=[name]),
            post=openapi.Operation(
                operation_id=f'{name}_create',
                responses=openapi.Responses({
                    '200': openapi.Response(
                        description='',
                        schema=_make_paginated_schema(entity.slug))}),
                parameters=_body_params(entity.slug),
                tags=[name]),
            parameters=[],
        )
        swagger.paths[f'/{name}/{{_uid}}/'] = openapi.PathItem(
            get=openapi.Operation(
                operation_id=f'{name}_read',
                responses=openapi.Responses({
                    '200': openapi.Response(
                        description='',
                        schema=_make_ref_schema(entity.slug))}),
                tags=[name]),
            put=openapi.Operation(
                operation_id=f'{name}_update',
                responses=openapi.Responses({
                    '200': openapi.Response(
                        description='',
                        schema=_make_ref_schema(entity.slug))}),
                parameters=_body_params(entity.slug),
                tags=[name]),
            patch=openapi.Operation(
                operation_id=f'{name}_partial_update',
                responses=openapi.Responses({
                    '200': openapi.Response(
                        description='',
                        schema=_make_ref_schema(entity.slug))}),
                parameters=_body_params(entity.slug),
                tags=[name]),
            delete=openapi.Operation(
                operation_id=f'{name}_delete',
                responses=openapi.Responses({
                    '204': openapi.Response(
                        description='')}),
                tags=[name]),
            parameters=[openapi.Parameter(**{
                'in_': 'path', 'name': '_uid', 'required': True,
                'type': 'string'
            })]
        )
    return swagger


def inject_backendless_routes(router):
    router.APIRootView = APIRootView
    router.get_urls = post_process_by(_add_backendless_urls)(router.get_urls)
    return router


def inject_backendless_schema():
    generator = swagger_settings.DEFAULT_GENERATOR_CLASS
    generator.get_schema = post_process_by(_add_schema)(generator.get_schema)
