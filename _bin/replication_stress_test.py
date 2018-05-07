import os
import sys

import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def django_setup():
    sys.path.insert(0, BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
    django.setup()


def after_django_setup():
    from contacts.models import Contact  # noqa

    # 1000 events ~= 224 seconds
    # ~ 4.5 events / second
    # ~ 0.22 second / event
    for _ in range(1000):
        contact = Contact.objects.order_by('?').first()
        contact.name = f'{contact.name.split()[0]} {contact.version}'
        contact.save()

if __name__ == '__main__':
    django_setup()
    after_django_setup()
