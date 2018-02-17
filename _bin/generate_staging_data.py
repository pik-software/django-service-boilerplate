import os
import sys

import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def django_setup():
    sys.path.insert(0, BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
    django.setup()


def after_django_setup():
    from django.contrib.auth.models import User  # noqa
    from contacts.tests.factories import ContactFactory  # noqa

    user, _ = User.objects.get_or_create(username='staging-superuser')
    user.is_staff = True
    user.is_superuser = True
    user.set_password('AwfnJAWkfjnawfkNAKA@(Afw1w')
    user.save()

    ContactFactory.create_batch(2000)


if __name__ == '__main__':
    django_setup()
    after_django_setup()
