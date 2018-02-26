import pytest
from django.test import TestCase

from core.mail import send_mail
from core.models import Email


class EmailTest(TestCase):

    def test_send_email_create_email_object(self):
        send_mail(
            subject='Subject',
            message='Message',
            recipient_list=(['to@example.com'],),
            from_email=['from@example.com'],
            context={'file': 'file_path'})

        emails = Email.objects.all()

        assert len(emails) == 1

    def test_send_email_without_recipient_list(self):
        with pytest.raises(ValueError) as error:
            send_mail(
                subject='Subject',
                message='Message',
                recipient_list='',
                from_email=['from@example.com'])

        assert 'No recipients in a list' in str(error)

    def test_send_email_with_context(self):
        with pytest.raises(ValueError) as error:
            send_mail(
                subject='Subject',
                message='Message',
                recipient_list=(['to@example.com'],),
                from_email=['from@example.com'],
                context='file')

        assert 'Invalid context argument' in str(error)
