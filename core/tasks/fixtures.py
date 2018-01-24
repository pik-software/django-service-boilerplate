from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


def create_user(email=None, password=None, **kwargs):
    User = get_user_model()  # noqa: pylint: invalid-name
    if not email:
        email = get_random_string() + "@test.com"
    u = User.objects.create(  # noqa: pylint: invalid-name
        email=email, username=get_random_string(),
        **kwargs)
    if password:
        u.set_password(password)
        u.save()
    return u


def get_user(pk):  # noqa: pylint: invalid-name
    User = get_user_model()  # noqa: pylint: invalid-name
    return User.objects.get(pk=pk)
