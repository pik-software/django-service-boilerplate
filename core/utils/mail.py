from typing import List
from dataclasses import dataclass

from django.core.mail import EmailMultiAlternatives


@dataclass
class EmailFileWrapper:

    content: str
    filename: str = None
    mimetype: str = None


class BaseEmailProducer:

    def __init__(
            self, emails_to: List, email_from: str, emails_cc: List = None,
            emails_bcc: List = None, files: List[EmailFileWrapper] = None):
        self._emails_to = emails_to
        self._email_from = email_from
        self._emails_cc = emails_cc
        self._emails_bcc = emails_bcc
        self._files = files

    def get_email_subject(self) -> str:
        return ''

    def get_plain_email_body(self) -> str:
        return ''

    def get_html_email_body(self) -> str:
        return ''

    def create_email(self) -> EmailMultiAlternatives:
        email = EmailMultiAlternatives(
            subject=self.get_email_subject(),
            body=self.get_plain_email_body(),
            from_email=self._email_from,
            to=self._emails_to, cc=self._emails_cc, bcc=self._emails_bcc)

        html_body = self.get_html_email_body()
        if html_body:
            email.attach_alternative(html_body, 'text/html')

        if self._files:
            for file_wrapper in self._files:
                email.attach(
                    filename=file_wrapper.filename,
                    content=file_wrapper.content,
                    mimetype=file_wrapper.mimetype)

        return email
