from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(BaseAppConfig):
    name = 'cors'
    verbose_name = _('Кросс-доменные запросы (CORS)')
