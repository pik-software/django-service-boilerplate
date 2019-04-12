import os
from os import mkdir
from os.path import join

from django.core.management.base import BaseCommand

from lib.codegen.generator import Generator

TEMPLATES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'codegen_templates',
)


def write_to_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def write_if_not_exists(path, content, force=False):
    if os.path.exists(path) and not force:
        return
    write_to_file(path, content)


def create_directory(path):
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
            '--force',
            action='store_true',
            help='Force overwrite existing files',
        )

    def handle(self, schema, app_name, **options):
        g = Generator(TEMPLATES, schema)
        force = options['force']
        create_directory(app_name)
        write_if_not_exists(
            join(app_name, '__init__.py'),
            '')
        write_to_file(
            join(app_name, 'abstract_schema_models.py'),
            g.generate('abstract_schema_models'))
        write_if_not_exists(
            join(app_name, 'models.py'),
            g.generate('models'),
            force=force)
