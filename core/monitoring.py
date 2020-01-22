import logging

import sentry_sdk


def alert(message: str, **kwargs) -> None:
    """
    Example:

        alert("webhook '{name}' response status={status}",
              name=subscription.name, status=webhook_status,
              user=subscription.user.pk, retry=self.retries,
              data=webhook_data)

    """
    text = message.format(**kwargs)
    sentry_sdk.capture_message(
        message=text, level=logging.ERROR)
