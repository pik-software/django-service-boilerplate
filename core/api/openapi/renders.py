import json

from django.utils.functional import Promise
from rest_framework.renderers import JSONOpenAPIRenderer


class JSONLazyObjEncoder(json.JSONEncoder):
    def default(self, obj):  # noqa: False positive method-hidden https://github.com/PyCQA/pylint/issues/414
        if isinstance(obj, Promise):
            return str(obj)
        return super().default(obj)


class JSONOpenAPILazyObjRenderer(JSONOpenAPIRenderer):
    """ Resolving proxy objects JSONOpenAPIRenderer

     DRF JSONOpenAPIRenderer fails on proxy objects within schema, using
     LazyObjEncoder

     """
    media_type = 'application/vnd.oai.openapi+json'
    charset = None
    format = 'openapi-json'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(
            data, indent=2, cls=JSONLazyObjEncoder).encode('utf-8')
