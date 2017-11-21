from django.conf import settings as django_settings


class _TemplateSettings(dict):
    def __init__(self, django_settings_wrapper, allowed):
        super().__init__()
        self.settings = django_settings_wrapper
        self.allowed_settings = set(allowed)

    def __getattr__(self, k):
        try:
            return self.__getitem__(k)
        except KeyError:
            raise AttributeError

    def __getitem__(self, k):
        if k not in self.allowed_settings:
            raise KeyError

        try:
            return getattr(self.settings, k)
        except AttributeError:
            return super().__getitem__(k)

    def __setitem__(self, k, v):
        self.allowed_settings.add(k)
        super().__setitem__(k, v)


def settings(request=None):
    """
    You can use settings variable in templates.

    Add this context_processors to `TEMPLATES` then set
    the `TEMPLATE_ACCESSIBLE_SETTINGS` add use any of this variables in
    templates:

        TEMPLATES = [
            {
                ...
                'OPTIONS': {
                    'context_processors': [
                        ...
                        'core.context_processors.django_settings',
                    ],
                },
            },
        ]

        TEMPLATE_ACCESSIBLE_SETTINGS = ['DEBUG']
    """
    allowed = getattr(django_settings, 'TEMPLATE_ACCESSIBLE_SETTINGS', [])
    template_settings = _TemplateSettings(django_settings, allowed)
    return {"settings": template_settings}
