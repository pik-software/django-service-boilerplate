import jinja2
from swagger_parser import SwaggerParser

from lib.codegen.utils import to_model_field, to_model_field_name, \
    skip_items_keys


class Generator:
    def __init__(self, templates, schema):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates),
            trim_blocks=True,
            lstrip_blocks=True)
        self.parser = SwaggerParser(swagger_path=schema)
        self.env.filters.update({
            'to_model_field': to_model_field,
            'to_model_field_name': to_model_field_name,
            'skip_items_keys': skip_items_keys,
        })

    def generate(self, name, options=None):
        return self.env.get_template(name + '.py').render({
            'schema': self.parser.specification,
            'options': options or {},
        })
