from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'cors'
    verbose_name = 'Кросс-доменные запросы (CORS)'
