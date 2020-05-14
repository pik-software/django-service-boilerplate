import logging
from copy import deepcopy

from django.db import transaction
from django.conf import settings
from django.core.management.base import BaseCommand

from lib.integra.models import UpdateState
from lib.integra.tasks import Integra


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Download integra updates for specific app model'

    def _get_integra_config(self, app_name, model_name):
        integra_configs = getattr(settings, 'INTEGRA_CONFIGS', [])

        if not integra_configs:
            raise ValueError('INTEGRA_CONFIGS is empty!')

        for config in integra_configs:
            for model_config in config['models']:
                app = model_config['app'].lower()
                model = model_config['model'].lower()
                if app == app_name and model == model_name:
                    config_copy = deepcopy(config)
                    config_copy['models'] = [model_config]
                    return config
        raise ValueError(
            f'Unknown app and/or model name: {app_name} {model_name}!')

    def add_arguments(self, parser):
        parser.add_argument('app', type=str)
        parser.add_argument('model', type=str)
        parser.add_argument('--clear-state', type=bool, default=False)

    def handle(self, *args, **options):
        app_name = options['app'].lower()
        model_name = options['model'].lower()
        config = self._get_integra_config(app_name, model_name)
        integrator = Integra(config)

        with transaction.atomic():
            if options['clear_state'] is True:
                key = f'{app_name}:{model_name}'
                UpdateState.objects.set_last_updated(key, None)

            processed = integrator.run()
            LOGGER.info(f'ok:{processed}')
