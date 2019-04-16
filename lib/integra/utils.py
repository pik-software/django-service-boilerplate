from copy import copy
from urllib.parse import urljoin

import requests

from core.utils.models import get_fields, has_field, get_model, \
    get_base_manager, get_pk_name
from .models import UpdateState


class Loader:
    """
    Example:

        l = Loader({
            'base_url': 'https://housing.pik-software.ru/',
            'request': {

            },
            'models': [
                {'url': '/api/v1/contact-list/',
                 'app': 'housing',
                 'model': 'contact'},
            ],
        })
    """
    def __init__(self, config):
        self.url = config['base_url']
        self.request = config['request']
        self.models = config['models']

    def download(self):
        for model in self.models:
            key = f'{model["app"]}:{model["model"]}'
            updated = UpdateState.objects.get_last_updated(key)
            for data in self._request(model, updated):
                yield data

    def _request(self, model, updated=None):
        app_name, model_name = model["app"], model["model"]
        url = urljoin(self.url, model['url'])
        auth = tuple(self.request['auth'].split(':', 1))
        url_params = {'ordering': 'updated'}
        if updated:
            url_params['updated__gte'] = updated.isoformat()
        for data in _fetch_data_from_api(url, auth, url_params):
            yield {
                'app': app_name,
                'model': model_name,
                'data': data,
                'last_updated': data['updated'] if 'updated' in data else None,
            }


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
    is_strict = True

    def __init__(self):
        self.last_updated = {}

    def update(self, obj):
        app = obj['app']
        model_name = obj['model']
        data = obj['data']
        assert isinstance(data, dict)
        obj_pk = data.pop('_uid', None)
        obj_type = data.pop('_type', None)
        obj_version = data.pop('_version', None)
        if obj_version:
            data['version'] = obj_version
        if not obj_pk:
            raise ValueError('protocol error: not obj[data][_uid]')
        if not obj_type and self.is_strict:
            raise ValueError('protocol error: not obj[data][_type]')
        if obj_type != model_name and self.is_strict:
            raise ValueError('protocol error: obj[data][_type] != obj[model]')

        model = get_model(app, model_name)
        pk_name = 'uid' if has_field(model, 'uid') else get_pk_name(model)
        instance = get_base_manager(model).filter(**{pk_name: obj_pk}).last()
        attrs = _prepare_model_attrs(model, data, self.is_strict)
        if instance:
            if obj_version and hasattr(instance, 'version') and \
                    instance.version and obj_version <= instance.version:
                return False
            for key, val in attrs.items():
                setattr(instance, key, val)
            instance.autoincrement_version = False
            instance.save()
        else:
            attrs[pk_name] = obj_pk
            get_base_manager(model).create(**attrs)

        self._set_last_updated(obj)
        return True

    def _set_last_updated(self, obj):
        last_updated = obj.get('last_updated')
        if last_updated:
            key = f'{obj["app"]}:{obj["model"]}'
            current_value = self.last_updated.get(key)
            if current_value and current_value > last_updated:
                raise ValueError('obj not in updated ordering')
            self.last_updated[key] = last_updated

    def flush_updates(self):
        for key, value in self.last_updated.items():
            UpdateState.objects.set_last_updated(key, value)
        self.clear_updates()

    def clear_updates(self):
        self.last_updated = {}


def _prepare_model_attrs(model, data, is_strict=True) -> dict:
    model_fields = get_fields(model)
    attributes = {}

    for field in model_fields:
        if field.name not in data:
            continue

        value = data[field.name]
        if field.is_relation:
            if isinstance(value, dict):
                if '_uid' not in value or ('_type' not in value and is_strict):
                    raise ValueError(f'protocol error: bad relation '
                                     f'obj[data][{field.name}]')
                value = value['_uid']
            rel_model = field.remote_field.model._meta.concrete_model  # noqa
            rel_model_kwargs = {'uid': value} \
                if has_field(rel_model, 'uid') \
                else {get_pk_name(rel_model): value}
            try:
                value = get_base_manager(rel_model).get(**rel_model_kwargs)
            except rel_model.DoesNotExist:
                raise ValueError(f'error: obj[data][{field.name}] '
                                 f'DoesNotExists')
        attributes[field.name] = value
    return attributes


def _fetch_data_from_api(url, auth, url_params=None):
    results = []
    next_page = 1
    url_params = copy(url_params) if url_params else {}
    while next_page:
        url_params['page'] = next_page
        response = requests.get(url, auth=auth, params=url_params)
        response.raise_for_status()
        data = response.json()
        next_page = data['page_next']
        for obj in data['results']:
            yield obj
    return results
