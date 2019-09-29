from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from .utils import Loader, Updater

LOGGER = get_task_logger(__name__)


class Integra:
    def __init__(self, config, ignore_version=False):
        self.models = config['models']
        self.loader = Loader(config)
        self.updater = Updater(ignore_version=ignore_version)

    def run(self):
        processed = 0
        updated = 0
        errors = 0
        for model in self.models:
            has_exception = False
            LOGGER.info(
                "integra: loading app=%s model=%s",
                model['app'], model['model'])
            for obj in self.loader.download(model):
                try:
                    processed += 1
                    status = self.updater.update(obj)
                    updated += 1 if status else 0
                except Exception as exc:  # noqa
                    has_exception = True
                    errors += 1
                    LOGGER.exception(
                        "integra error: %r; app=%s model=%s data=%r",
                        exc, obj['app'], obj['model'], obj['data'])
            if not has_exception:
                self.updater.flush_updates()
            self.updater.clear_updates()
        return processed, updated, errors


@shared_task
def download_updates():
    processed, updated, errors = 0, 0, 0
    configs = getattr(settings, 'INTEGRA_CONFIGS', None)
    if not configs:
        return 'no-configs'
    for config in configs:
        integrator = Integra(config)
        c_processed, c_updated, c_errors = integrator.run()
        processed += c_processed
        updated += c_updated
        errors += c_errors
    return f'ok:{processed}/{updated}:errors:{errors}'
