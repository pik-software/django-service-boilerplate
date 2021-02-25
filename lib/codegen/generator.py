import jinja2
from prance import BaseParser

from lib.codegen.utils import to_model_field_name, skip_items_keys
from lib.codegen.model_field_generator import ModelFieldGenerator


class Generator:
    MAJOR_VERSION = 0

    def __init__(self, templates, schema):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates),
            trim_blocks=True,
            lstrip_blocks=True)
        self.parser = BaseParser(
            schema, backend='openapi-spec-validator', strict=False)
        self.env.filters.update({
            'to_model_field': ModelFieldGenerator(),
            'to_model_field_name': to_model_field_name,
            'skip_items_keys': skip_items_keys,
        })

    def get_version(self):
        return self.parser.version_parsed[self.MAJOR_VERSION]

    def get_v2_definitions(self):
        return self.parser.specification['definitions']

    def get_v3_definitions(self):
        return self.parser.specification['components']['schemas']

    def get_definitions(self):
        version = self.get_version()
        if version == 2:
            return self.get_v2_definitions()
        if version == 3:
            return self.get_v3_definitions()
        raise Exception(f'Unknown schema version - {self.parser.version}')

    def generate(self, name, options=None):
        return self.env.get_template(name + '.j2').render({
            'definitions': self.get_definitions(),
            'options': options or {},
        })
