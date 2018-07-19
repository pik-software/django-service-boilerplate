import os


_CONFLICT_SETTINGS = [
    'SOCIAL_AUTH_PIPELINE'
]

_REQUIRED_SETTINGS = [
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'AUTHENTICATION_BACKENDS',
]


class UnknownSequenceType(Exception):
    pass


class RequiredSettingMissing(Exception):
    pass


class ConflictSetting(Exception):
    pass


class RequiredSequenceItemMissing(Exception):
    pass


class SequenceItemAlreadyDefined(Exception):
    pass


def _to_list(sequence, name):
    """ Cast sequence to list

    >>> _to_list((), 'TEST')
    []

    >>> _to_list([], 'TEST')
    []

    >>> _to_list(set(), 'TEST')
    Traceback (most recent call last):
        ...
    settings.UnknownSequenceType: Unknown sequence type <class 'set'> of TEST, list or tuple expected

    """


    if isinstance(sequence, list):
        return sequence
    if isinstance(sequence, tuple):
        return list(sequence)
    raise UnknownSequenceType(
        f'Unknown sequence type {type(sequence)} of {name}, '
        f'list or tuple expected')


def _to_original(sequence, result):
    """ Cast result into the same type

    >>> _to_original([], ())
    []

    >>> _to_original((), [])
    ()

    """

    if isinstance(sequence, tuple):
        return tuple(result)
    if isinstance(sequence, list):
        return list(result)

    return result


def _append(settings, name, value):
    """ Prepend item into the settings sequence

    >>> settings = {'TEST': ['b', 'c']}
    >>> _append(settings, 'TEST', 'a')
    >>> settings
    {'TEST': ['b', 'c', 'a']}

    >>> settings = {'TEST': ('b', 'c')}
    >>> _append(settings, 'TEST', 'a')
    >>> settings
    {'TEST': ('b', 'c', 'a')}

    >>> settings = {'TEST': ['b', 'c']}
    >>> _append(settings, 'TEST', 'c')
    Traceback (most recent call last):
        ...
    settings.SequenceItemAlreadyDefined: Sequence c value is already defined in setting TEST

    """

    sequence = settings.get(name, ())
    result = _to_list(sequence, name)
    if value in result:
        raise SequenceItemAlreadyDefined(f'Sequence {value} value is already defined in setting {name}')

    result.append(value)
    if isinstance(sequence, tuple):
        result = tuple(result)

    settings[name] = _to_original(sequence, result)


def _prepend(settings, name, value):
    """ Prepend item into the settings sequence

    >>> settings = {'TEST': ['b', 'c']}
    >>> _prepend(settings, 'TEST', 'a')
    >>> settings
    {'TEST': ['a', 'b', 'c']}

    >>> settings = {'TEST': ('b', 'c')}
    >>> _prepend(settings, 'TEST', 'a')
    >>> settings
    {'TEST': ('a', 'b', 'c')}

    >>> settings = {'TEST': ['b', 'c']}
    >>> _prepend(settings, 'TEST', 'c')
    Traceback (most recent call last):
        ...
    settings.SequenceItemAlreadyDefined: Sequence c value is already defined in setting TEST

    """

    sequence = settings.get(name, ())
    result = _to_list(sequence, name)
    if value in result:
        raise SequenceItemAlreadyDefined(f'Sequence {value} value is already defined in setting {name}')

    result.insert(0, value)
    settings[name] = _to_original(sequence, result)


def _insert(settings, name, after, value):
    """ Insert item into sequence setting

    >>> settings = {'TEST': ['a']}
    >>> _insert(settings, 'TEST', 'a', 'b')
    >>> settings
    {'TEST': ['a', 'b']}

    >>> settings = {'TEST': ('a', )}
    >>> _insert(settings, 'TEST', 'a', 'b')
    >>> settings
    {'TEST': ('a', 'b')}

    >>> settings = {'TEST': ['a']}
    >>> _insert(settings, 'TEST', 'c', 'b')
    Traceback (most recent call last):
        ...
    settings.RequiredSequenceItemMissing: Required item c missing form setting TEST

    >>> settings = {'TEST': ['a', 'b']}
    >>> _insert(settings, 'TEST', 'a', 'b')
    Traceback (most recent call last):
        ...
    settings.SequenceItemAlreadyDefined: Sequence item b is already defined in setting TEST

    """

    sequence = settings.get(name, ())
    result = _to_list(sequence, name)
    if value in result:
        raise SequenceItemAlreadyDefined(f'Sequence item {value} is already defined in setting {name}')

    try:
        index = sequence.index(after) + 1
    except ValueError:
        raise RequiredSequenceItemMissing(f'Required item {after} missing form setting {name}' )

    result.insert(index, value)
    settings[name] = _to_original(sequence, result)


def _set_from_env(settings, name, default=None, delimiter=None):
    """ Extract setting from ENV, predefined or default

    >>> settings = {}
    >>> _set_from_env(settings, 'test', 'default')
    >>> settings
    {'test': 'default'}

    >>> settings = {'test': '1,2'}
    >>> _set_from_env(settings, 'test', 'default', delimiter=',')
    >>> settings
    {'test': ['1', '2']}

    >>> settings = {'test': 'predefined'}
    >>> _set_from_env(settings, 'test', 'default')
    >>> settings
    {'test': 'predefined'}

    >>> settings = {}
    >>> os.environ['test'] = 'env'
    >>> _set_from_env(settings, 'test', 'default')
    >>> settings
    {'test': 'env'}

     """

    value = os.environ.get(name, settings.get(name, default))
    if delimiter is not None:
        value = value.split(delimiter)
    settings[name] = value


def _check_settings(settings):
    """ Check settings compatibility

    >>> _check_settings({})
    Traceback (most recent call last):
        ...
    settings.RequiredSettingMissing: Explicit settings.INSTALLED_APPS definition required

    >>> _check_settings({'INSTALLED_APPS': [], 'MIDDLEWARE': [], 'AUTHENTICATION_BACKENDS': [], 'SOCIAL_AUTH_PIPELINE': []})
    Traceback (most recent call last):
        ...
    settings.ConflictSetting: Setting SOCIAL_AUTH_PIPELINE have to be defined by set_oidc_settings() only

    >>> _check_settings({'INSTALLED_APPS': [], 'MIDDLEWARE': [], 'AUTHENTICATION_BACKENDS': []})



    :param settings:
    :return:
    """
    for setting in _REQUIRED_SETTINGS:
        if setting in settings:
            continue
        raise RequiredSettingMissing(
            f'Explicit settings.{setting} definition required')

    for setting in _CONFLICT_SETTINGS:
        if setting not in settings:
            continue
        raise ConflictSetting(
            f"Setting {setting} have to be defined by set_oidc_settings() "
            f"only")


def set_oidc_settings(settings):
    _check_settings(settings)

    _append(settings, 'INSTALLED_APPS', 'social_django')

    _insert(settings, 'MIDDLEWARE',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'lib.oidc_relied.middleware.OIDCExceptionMiddleware')

    _append(settings, 'AUTHENTICATION_BACKENDS',
            'lib.oidc_relied.backends.PIKOpenIdConnectAuth')

    if 'rest_framework' in settings['INSTALLED_APPS']:
        if 'DEFAULT_AUTHENTICATION_CLASSES' not in settings['REST_FRAMEWORK']:
            raise RequiredSettingMissing(
                'Explicit REST_FRAMEWORK[\'DEFAULT_AUTHENTICATION_CLASSES\'] '
                'definition expected')
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
