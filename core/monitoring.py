import logging
from raven.contrib.django.models import client


def alert(message: str, **kwargs) -> None:
    """
    Example:

        alert("webhook '{name}' response status={status}",
              name=subscription.name, status=webhook_status,
              user=subscription.user.pk, retry=self.retries,
              data=webhook_data)

    """
    tags = {k: v for k, v in kwargs.items() if f'{{{k}}}' in message}
    extra = {k: v for k, v in kwargs.items() if f'{{{k}}}' not in message}
    text = message.format(**kwargs)
    client.captureMessage(
        message=text, extra=extra, tags=tags,
        level=logging.ERROR)
