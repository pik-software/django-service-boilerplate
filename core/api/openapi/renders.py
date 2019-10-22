import json

from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.utils.encoders import JSONEncoder


class JSONOpenAPILazyObjRenderer(JSONOpenAPIRenderer):
    """ Resolving proxy objects JSONOpenAPIRenderer

     DRF JSONOpenAPIRenderer fails on proxy objects within schema, using
     drf.JSONEncoder

     """
    media_type = 'application/vnd.oai.openapi+json'
    charset = None
    format = 'openapi-json'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(
            data, indent=2, cls=JSONEncoder).encode('utf-8')
