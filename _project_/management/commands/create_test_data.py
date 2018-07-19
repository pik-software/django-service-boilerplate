import logging

from django.core.management.base import BaseCommand

from contacts.tests.factories import ContactFactory


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Create objects to populate DB with some test data'

    def handle(self, *args, **options):
        ContactFactory.create_batch(2000)
