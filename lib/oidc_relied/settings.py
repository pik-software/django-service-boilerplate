import os


_REQUIRED_SETTINGS = [
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'AUTHENTICATION_BACKENDS',
]


class UnknownSequenceType(Exception):
    pass


class RequiredSettingMissing(Exception):
    pass


class RequiredItemMissing(Exception):
    pass


class ItemAlreadyExists(Exception):
    pass


def _to_list(sequence):
    if isinstance(sequence, list):
        return sequence
    if isinstance(sequence, tuple):
        return list(sequence)
    raise UnknownSequenceType(type(sequence))


def _to_original(sequence, result):
    if isinstance(sequence, tuple):
        return tuple(result)
    return result


def _append(settings, name, value):
    sequence = settings.get(name, ())
    result = _to_list(sequence)
    if name in result:
        raise ItemAlreadyExists(name)

    result.append(value)
    if isinstance(sequence, tuple):
        result = tuple(result)

    settings[name] = _to_original(sequence, result)


def _prepend(settings, name, value):
    sequence = settings.get(name, ())
    result = _to_list(sequence)
    if name in result:
        raise ItemAlreadyExists(name)

    result.insert(0, value)
    settings[name] = _to_original(sequence, result)


def _insert(settings, name, after, value):
    sequence = settings.get(name, ())
    result = _to_list(sequence)
    if name in result:
        raise ItemAlreadyExists(name)

    index = sequence.index(after)
    if index is None:
        raise RequiredItemMissing(after)

    result.insert(index, value)
    settings[name] = _to_original(sequence, result)

    settings[name] = result


def _set_from_env(settings, name, default=None, delimiter=' ', multiple=False):
    value = os.environ.get(name, settings.get(name, default))
    if multiple:
        value = value.split(delimiter)
    settings[name] = value


def _check_required_settings(settings):
    for setting in _REQUIRED_SETTINGS:
        if setting in settings:
            continue
        raise RequiredSettingMissing(setting)


def set_oidc_settings(settings):
    _check_required_settings(settings)

    _append(settings, 'INSTALLED_APPS', 'social_django')

    _insert(settings, 'MIDDLEWARE',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'lib.oidc_relied.middleware.OIDCExceptionMiddleware')

    _append(settings, 'AUTHENTICATION_BACKENDS',
            'lib.oidc_relied.backends.PIKOpenIdConnectAuth')

    if 'rest_framework' in settings['INSTALLED_APPS']:
        settings.setdefault('REST_FRAMEWORK', dict())
        _append(
            settings['REST_FRAMEWORK'], 'DEFAULT_AUTHENTICATION_CLASSES',
            'rest_framework_social_oauth2.authentication.SocialAuthentication')

    _set_from_env(settings, 'OIDC_PIK_ENDPOINT',
                  default='http://auth.pik-software.ru/openid')
    _set_from_env(settings, 'OIDC_PIK_CLIENT_ID')
    _set_from_env(settings, 'OIDC_PIK_CLIENT_SECRET')

    if settings.get('OIDC_PIK_CLIENT_ID') is not None:
        settings.setdefault('LOGIN_URL', '/openid/login/pik/')
    else:
        settings.setdefault('LOGIN_URL', 'login')

    settings.setdefault('SOCIAL_AUTH_POSTGRES_JSONFIELD', True)

    settings.setdefault('SOCIAL_AUTH_PIPELINE', (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        # 'social_core.pipeline.mail.mail_validation',
        'social_core.pipeline.social_auth.associate_by_email',
        'lib.oidc_relied.pipeline.associate_by_username',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.user.create_user',
        'lib.oidc_relied.pipeline.actualize_roles',

        # TODO: Remove after SPA
        'lib.oidc_relied.pipeline.actualize_staff_status',

        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
    ))
