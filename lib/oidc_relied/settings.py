import os


class UnknownSequenceType(Exception):
    pass


class RequiredItemMissing(Exception):
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
    sequence = settings[name]

    result = _to_list(sequence)

    result.append(value)
    if isinstance(sequence, tuple):
        result = tuple(result)

    settings[name] = _to_original(sequence, result)


def _prepend(settings, name, value):
    sequence = settings[name]

    result = _to_list(sequence)
    result.insert(0, value)
    settings[name] = _to_original(sequence, result)


def _insert(settings, name, after, value):
    sequence = settings[name]

    result = _to_list(sequence)

    index = sequence.index(after)
    if index is None:
        raise RequiredItemMissing(after)

    result.insert(index, value)
    settings[name] = _to_original(sequence, result)

    settings[name] = result


def _set_from_env(settings, name, default=None, delimiter=' ', multiple=False):
    value = os.environ.get(name, default)
    if multiple:
        value = value.split(delimiter)
    settings[name] = value


def apply_oidc_settings(settings):
    _append(settings, 'INSTALLED_APPS', 'social_django')

    after = 'django.contrib.sessions.middleware.SessionMiddleware'
    _insert(settings, 'MIDDLEWARE', after,
            'cors.middleware.CachedCorsMiddleware')
    _insert(settings, 'MIDDLEWARE', after,
            'lib.oidc_relied.middleware.OIDCExceptionMiddleware')

    _append(settings, 'AUTHENTICATION_BACKENDS',
            'lib.oidc_relied.backends.PIKOpenIdConnectAuth')

    _append(settings['REST_FRAMEWORK'], 'DEFAULT_AUTHENTICATION_CLASSES',
            'rest_framework_social_oauth2.authentication.SocialAuthentication')

    _set_from_env(settings, 'OIDC_PIK_ENDPOINT',
                  default='http://auth.pik-software.ru/openid')
    _set_from_env(settings, 'OIDC_PIK_CLIENT_ID')
    _set_from_env(settings, 'OIDC_PIK_CLIENT_SECRET')

    settings['LOGIN_URL'] = 'login'
    if settings['OIDC_PIK_CLIENT_ID'] is not None:
        settings['LOGIN_URL'] = '/openid/login/pik/'

    settings['SOCIAL_AUTH_POSTGRES_JSONFIELD'] = True

    settings['SOCIAL_AUTH_PIPELINE'] = (
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
    )
