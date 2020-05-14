from copy import copy
from urllib.parse import urljoin

import requests

from core.utils.models import (
    get_fields, has_field, get_model, get_base_manager, get_pk_name)
from .models import UpdateState


class Loader:
    """
    Example:

        l = Loader({
            'base_url': 'https://housing.pik-software.ru/',
            'request': {
                'auth': 'login:password',
            },
            'models': [
                {'url': '/api/v1/contact-list/',
                 'app': 'housing',
                 'model': 'contact'},
            ],
        })
    """
    DEFAULT_ORDERING = 'updated'

    def __init__(self, config):
        self.url = config['base_url']
        self.request = config['request']

    def _get_key(self, model):
        return f'{model["app"]}:{model["model"]}'

    def download(self, model):
        key = self._get_key(model)
        updated = UpdateState.objects.get_last_updated(key)
        for data in self._request(model, updated):
            yield data

    def _request(self, model, updated=None):
        ordering = model.get('ordering', self.DEFAULT_ORDERING)
        url = urljoin(self.url, model['url'])
        auth = tuple(self.request['auth'].split(':', 1))
        url_params = {'ordering': ordering}
        if updated:
            url_params['updated__gte'] = updated.isoformat()
        for data in _fetch_data_from_api(url, auth, url_params):
            yield data


class Updater:
    """
    Example:

        u = Updater()
        u.update(
            {'app': 'housing',
             'model': 'contact',
             'last_updated': None,
             'data': {'_uid': 'x...', '_type': 'contact', ...}},
        )
    """

    def __init__(self, app, model_name, is_strict=None):
        self.app = app
        self.model_name = model_name
        self.last_updated = None
        self.is_strict = True if is_strict is None else is_strict

    def __str__(self):
        return f'{self.app}:{self.model_name}:{self.last_updated}'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            self._update_last_updated()

    def _get_key_for_model_config(self):
        return f'{self.app}:{self.model_name}'

    def _set_last_updated(self, updated):
        if self.last_updated is None or self.last_updated < updated:
            self.last_updated = updated

    def _update_last_updated(self):
        if self.last_updated:
            key = self._get_key_for_model_config()
            UpdateState.objects.set_last_updated(key, self.last_updated)

    def _get_filter_params(self, obj_pk, model):
        pk_name = 'uid' if has_field(model, 'uid') else get_pk_name(model)
        return {pk_name: obj_pk}

    def _get_rel_model_filter_kwargs(self, rel_model, value):  # noqa: maybe-static
        return (
            {'uid': value} if has_field(rel_model, 'uid')
            else {get_pk_name(rel_model): value})

    def _prepare_model_attrs(self, model, data):
        model_fields = get_fields(model)
        attributes = {}

        for field in model_fields:
            if field.name not in data:
                continue

            if not field.concrete:
                # Ignore reverse relation fields
                continue

            value = data[field.name]
            if field.is_relation and value:
                if isinstance(value, dict):
                    if '_uid' not in value or (
                            '_type' not in value and self.is_strict):
                        raise ValueError(f'protocol error: bad relation '
                                         f'obj[data][{field.name}]')
                    value = value['_uid']
                rel_model = field.remote_field.model._meta.concrete_model  # noqa
                rel_model_kwargs = self._get_rel_model_filter_kwargs(
                    rel_model, value)
                try:
                    value = get_base_manager(rel_model).get(**rel_model_kwargs)
                except rel_model.DoesNotExist:
                    if self.is_strict:
                        raise ValueError(
                            f'error: obj[data][{field.name}] DoesNotExists')
                    attrs = _get_attrs_from_link(data[field.name])
                    value = get_base_manager(model).create(**attrs)
            attributes[field.name] = value
        return attributes

    def update(self, data):
        obj_pk = data.pop('_uid', None)
        obj_type = data.pop('_type', None)
        obj_version = data.pop('_version', None)
        if obj_version:
            data['version'] = obj_version
        if not obj_pk:
            raise ValueError('protocol error: not obj[data][_uid]')
        if not obj_type and self.is_strict:
            raise ValueError('protocol error: not obj[data][_type]')
        if obj_type != self.model_name and self.is_strict:
            raise ValueError('protocol error: obj[data][_type] != obj[model]')

        model = get_model(self.app, self.model_name)
        pk_name = 'uid' if has_field(model, 'uid') else get_pk_name(model)
        filter_params = self._get_filter_params(obj_pk, model)
        instance = get_base_manager(model).filter(**filter_params).last()
        attrs = self._prepare_model_attrs(model, data)
        if instance:
            if (obj_version and hasattr(instance, 'version')
                    and instance.version
                    and obj_version <= instance.version):
                return False
            for key, val in attrs.items():
                setattr(instance, key, val)
            instance.autoincrement_version = False
            instance.save()
        else:
            attrs[pk_name] = obj_pk
            instance = get_base_manager(model).create(**attrs)

        self._set_last_updated(instance.updated)
        return True


def _get_attrs_from_link(link: dict) -> dict:
    return {
        'uid': link['_uid'],
        'created': link.get('created'),
        'updated': link.get('updated'),
        'deleted': link.get('deleted'),
        'version': link.get('version'),
    }


def _fetch_data_from_api(url, auth, url_params=None):
    next_page = 1
    url_params = copy(url_params) if url_params else {}
    while next_page:
        url_params['page'] = next_page
        response = requests.get(url, auth=auth, params=url_params)
        response.raise_for_status()
        data = response.json()
        next_page = data.get('page_next')
        for obj in data['results']:
            yield obj
