import os


__all__ = [
    'OIDC_PIK_ENDPOINT', 'OIDC_PIK_CLIENT_ID', 'OIDC_PIK_CLIENT_SECRET',
    'LOGIN_URL', 'SOCIAL_AUTH_POSTGRES_JSONFIELD', 'SOCIAL_AUTH_PIPELINE']


OIDC_PIK_ENDPOINT = os.environ.get('OIDC_PIK_ENDPOINT',
                                   f'http://auth.pik-software.ru/openid')
OIDC_PIK_CLIENT_ID = os.environ.get('OIDC_PIK_CLIENT_ID', None)
OIDC_PIK_CLIENT_SECRET = os.environ.get('OIDC_PIK_CLIENT_SECRET', None)


LOGIN_URL = 'login'
if OIDC_PIK_CLIENT_ID is not None:
    LOGIN_URL = '/openid/login/pik/'


SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_PIPELINE = (
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
