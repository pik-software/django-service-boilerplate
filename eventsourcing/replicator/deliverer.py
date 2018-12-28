import logging

import requests

from ..utils import ReplicatorDeliveryError

LOGGER = logging.getLogger(__name__)


def _deliver(user, settings, serialized_data) -> None:
    url, kwargs = _prepare_webhook_request_kwargs(settings)
    data = serialized_data.encode('utf-8')
    LOGGER.info('do webhook request url="%s"; %r', url, kwargs)
    try:
        response = requests.post(url, data=data, timeout=10, **kwargs)
    except requests.RequestException as exc:
        raise ReplicatorDeliveryError('connection problem', {
            'response_status': 0,
            'response_content': repr(exc),
        })

    code, content = response.status_code, response.content
    LOGGER.info('webhook response status_code=%s %r', code, content)
    if code != 200:
        raise ReplicatorDeliveryError('status != 200', {
            'response_status': code,
            'response_content': content,
        })


def _prepare_webhook_request_kwargs(settings):
    webhook_url = settings['webhook_url']
    webhook_cookies = settings.get('webhook_cookies', None)
    webhook_headers = settings.get('webhook_headers', {})
    webhook_headers['content-type'] = 'application/json'
    webhook_auth = settings.get('webhook_auth', None)
    if webhook_auth and isinstance(webhook_auth, list):
        # convert to requests auth tuple
        webhook_auth = tuple(webhook_auth)
    return webhook_url, dict(
        auth=webhook_auth, headers=webhook_headers, cookies=webhook_cookies,
    )
