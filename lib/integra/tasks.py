from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from .utils import Loader, Updater

LOGGER = get_task_logger(__name__)


class Integra:
    def __init__(self, config):
        self.models = config['models']
        self.loader = Loader(config)
        self.updater = Updater()

    def run(self):
        count = 0
        for model in self.models:
            has_exception = False
            LOGGER.info(
                "integra: loading app=%s model=%s",
                model['app'], model['model'])
            for obj in self.loader.download(model):
                try:
                    status = self.updater.update(obj)
                    count += 1 if status else 0
                except Exception as exc:  # noqa
                    LOGGER.exception(
                        "integra error: %r; app=%s model=%s data=%r",
                        exc, obj['app'], obj['model'], obj['data'])
                    has_exception = True
            if not has_exception:
                self.updater.flush_updates()
            self.updater.clear_updates()
        return count


@shared_task
def download_updates():
    count = 0
    configs = getattr(settings, 'INTEGRA_CONFIGS', None)
    if not configs:
        return 'no-configs'
    for config in configs:
        integrator = Integra(config)
        count += integrator.run()
    return f'ok:{count}'
