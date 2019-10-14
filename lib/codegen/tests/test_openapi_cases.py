import os

import pytest

from lib.codegen.generator import Generator

TEMPLATES = os.path.join(
    (os.path.dirname(os.path.dirname(__file__))),
    'codegen_templates',
)

SCHEMA = os.path.join(
    ((os.path.dirname(__file__))),
    'testcases', 'openapi3', 'openapi3.json'
)


@pytest.fixture(params=[
    (SCHEMA, 'models', f'{SCHEMA}.models.py'),
    (SCHEMA, 'abstract_schema_models', f'{SCHEMA}.abstract_schema_models.py'),
])
def cases(request):
    return request.param


def _read_from_file(path):
    with open(path) as fileobj:
        return fileobj.read()


def test_generate_models(cases):
    schema, template, result = cases
    generator = Generator(TEMPLATES, schema)
    assert generator.generate(template) == _read_from_file(result)
