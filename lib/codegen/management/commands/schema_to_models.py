import json
import os
import shlex
import sys
from os import mkdir
from os.path import join

from django.core.management.base import BaseCommand

from lib.codegen.generator import Generator

TEMPLATES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'codegen_templates',
)


def _write_to_file(path, content):
    with open(path, 'w') as fileobj:
        fileobj.write(content)


def _write_if_not_exists(path, content, force=False):
    if os.path.exists(path) and not force:
        return
    _write_to_file(path, content)


def _create_directory(path):
    try:
        mkdir(path)
    except FileExistsError:
        pass


class Command(BaseCommand):
    help = 'Generate application by OpenAPI schema'

    def add_arguments(self, parser):
        parser.add_argument('schema')
        parser.add_argument('app_name')
        parser.add_argument(
            '--options',
            default={},
            type=lambda x: dict(json.loads(x)),
            help='Extra template generation options (json obj format)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing files',
        )

    def _add_extra_options(self, options):
        command = ' '.join(['python'] + [shlex.quote(s) for s in sys.argv])
        options['command'] = command

    def handle(self, schema, app_name, **options):
        generator = Generator(TEMPLATES, schema)
        self._add_extra_options(options['options'])

        _create_directory(app_name)
        _write_if_not_exists(
            join(app_name, '__init__.py'),
            '')
        _write_to_file(
            join(app_name, 'abstract_schema_models.py'),
            generator.generate('abstract_schema_models', options['options']))
        _write_if_not_exists(
            join(app_name, 'models.py'),
            generator.generate('models', options['options']),
            force=options['force'])
