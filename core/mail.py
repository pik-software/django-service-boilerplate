from collections import OrderedDict

from django.core.mail.message import EmailMessage

from core.models import Email


def send_mail(
        subject, message, from_email, recipient_list, contents=None, *,
        context=None):
    if len(recipient_list) < 1:
        raise ValueError('No recipients in a list')
    if context and not isinstance(context, (dict, OrderedDict)):
        raise ValueError('Invalid context argument')
    new_email = EmailMessage()  # noqa: pylint=invalid-name
    new_email.subject = subject
    new_email.from_email = from_email
    new_email.to = recipient_list
    new_email.body = message
    email_instance = Email(
        email_from=new_email.from_email,
        email_to=new_email.to,
        subject=new_email.subject,
        body=new_email.body,
        context=context,
    )
    email_instance.save()
    if contents:
        for filename in contents:
            new_email.attach(filename, contents[filename])
    try:
        new_email.send()
    except Exception as error:  # noqa: pylint=broad-except
        email_instance.error_message = repr(error)
        email_instance.save()
