from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext as _


class AppConfig(BaseAppConfig):
    name = 'contacts'
    verbose_name = _('Общие контакты')
