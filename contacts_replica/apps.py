from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(BaseAppConfig):
    name = 'contacts_replica'
    verbose_name = _('Общие контакты (replica)')
