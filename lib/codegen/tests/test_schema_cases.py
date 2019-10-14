import os

import pytest

from lib.codegen.generator import Generator

TEMPLATES = os.path.join(
    (os.path.dirname(os.path.dirname(__file__))),
    'codegen_templates',
)

SWAGGER_SCHEMA = os.path.join(
    os.path.dirname(__file__),
    'testcases', 'swagger2', 'swagger2.json'
)

OPENAPI_SCHEMA = os.path.join(
    ((os.path.dirname(__file__))),
    'testcases', 'openapi3', 'openapi3.json'
)


@pytest.fixture(params=[
    (SWAGGER_SCHEMA, 'models', f'{SWAGGER_SCHEMA}.models.py'),
    (SWAGGER_SCHEMA, 'abstract_schema_models',
     f'{SWAGGER_SCHEMA}.abstract_schema_models.py'),
    (OPENAPI_SCHEMA, 'models', f'{OPENAPI_SCHEMA}.models.py'),
    (OPENAPI_SCHEMA, 'abstract_schema_models',
     f'{OPENAPI_SCHEMA}.abstract_schema_models.py'),
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
