from time import time

import requests
from bs4 import BeautifulSoup

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group

from core.metrics import increment, timing

LOGIN_URL = 'https://rm.pik.ru/login?back_url=http%3A%2F%2Frm.pik.ru%2F'


def is_correct_credentials(username, password):
    session = requests.session()
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    token = soup.find(attrs={"name": "authenticity_token"})['value']
    back_url = soup.find(attrs={"name": "back_url"})['value']
    data = {
        'authenticity_token': token,
        'username': username,
        'password': password,
        'back_url': back_url,
        'login': 'Login &#187;',
        'utf8': '&#x2713;',
    }
    response = session.post(LOGIN_URL, data)
    data = response.content.decode('utf-8').lower()
    is_login = (('зарегистрируйтесь' not in data) and ('выйти' in data) and
                response.status_code == 200)
    return is_login


class RemoteUserBackend(ModelBackend):
    create_unknown_user = True

    def authenticate(self, username=None, password=None, **kwargs):  # noqa: pylint=arguments-differ
        user = None
        username = self.clean_username(username)

        start_check_credentials_time = time()
        is_correct = is_correct_credentials(username, password)
        end_check_credentials_time = time()
        dt = end_check_credentials_time - start_check_credentials_time  # noqa

        metrics_tags = ['correct:' + str(is_correct).lower()]
        increment('ldap.authenticate', tags=metrics_tags)
        timing('ldap.is_correct_credentials', dt, tags=metrics_tags)
        if not is_correct:
            return

        UserModel = get_user_model()  # noqa pylint=invalid-name

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = UserModel._default_manager.get_or_create(**{  # noqa: pylint=protected-access
                UserModel.USERNAME_FIELD: username
            })
            if created:
                user = self.configure_user(user)
                user.save()
                default, _ = Group.objects.get_or_create(name='default')
                default.user_set.add(user)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)  # noqa: pylint=protected-access
            except UserModel.DoesNotExist:
                pass
        return user if self.user_can_authenticate(user) else None

    def clean_username(self, username):  # noqa: pylint=no-self-use
        if username and isinstance(username, str):
            if '@pik-comfort.ru' in username:
                username = username.rstrip('@pik-comfort.ru')
            return username.lower()
        return username

    def configure_user(self, user):  # noqa: pylint=no-self-use
        user.email = user.username + '@pik-comfort.ru'
        user.is_staff = True
        return user
