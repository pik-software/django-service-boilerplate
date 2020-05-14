from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import transaction
from sentry_sdk import capture_exception

from .utils import Loader, Updater
from .models import UpdateState


LOGGER = get_task_logger(__name__)


class Integra:
    LOADER_CLS = Loader
    UPDATER_CLS = Updater

    def __init__(self, config):
        self.config = config

    def _update_model(self, model_config):
        app = model_config['app']
        model_name = model_config['model']
        key = self._get_key(model_config)
        last_updated = UpdateState.objects.get_last_updated(key)
        LOGGER.info(
            'loading app=%s model=%s last_updated: %s', app, model_name,
            last_updated)
        processed = self._process(model_config)
        LOGGER.info(
            'loading complete app %s, model %s, processed: %s', app,
            model_name, processed)
        return processed

    def _get_key(self, model_config):  # noqa: maybe-static
        app = model_config['app']
        model_name = model_config['model']
        return f'{app}:{model_name}'

    def _process(self, model_config):
        processed = 0
        loader = self.LOADER_CLS(self.config)
        with self.UPDATER_CLS(
                model_config['app'], model_config['model'],
                model_config.get('is_strict')) as updater:
            for obj in loader.download(model_config):
                updater.update(obj)
                processed += 1
        return processed

    def run(self):
        total_processed = 0

        for model_config in self.config['models']:
            with transaction.atomic():
                try:
                    processed = self._update_model(model_config)
                except Exception as exc:  # noqa: pylint==broad-except
                    LOGGER.exception(exc)
                    capture_exception(exc)
                    continue

            total_processed += processed
        return total_processed


@shared_task
def download_updates():
    configs = getattr(settings, 'INTEGRA_CONFIGS', None)
    total_processed = 0

    for config in configs:
        integrator = Integra(config)
        total_processed += integrator.run()

    LOGGER.info('All models updated, total records: %s', total_processed)
