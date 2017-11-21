from django.conf import settings
from datadog import DogStatsd

_STATSD = DogStatsd(host=settings.DD_STATSD_ADDR, port=settings.DD_STATSD_PORT,
                    namespace=settings.DD_STATSD_NAMESPACE)


def gauge(metric, value, tags=None):
    """
    Record the value of a gauge, optionally setting a list of tags and a
    sample rate.

    >>> gauge('users.online', 123)
    >>> gauge('active.connections', 1001, tags=["protocol:http"])
    """
    _STATSD.gauge(metric, value=value, tags=tags)


def increment(metric, value=1, tags=None):
    """
    Increment a counter, optionally setting a value, tags and a sample
    rate.

    >>> increment('page.views')
    >>> increment('files.transferred', 124)
    """
    _STATSD.increment(metric, value=value, tags=tags)


def decrement(metric, value=1, tags=None):
    """
    Decrement a counter, optionally setting a value, tags and a sample
    rate.

    >>> decrement('files.remaining')
    >>> decrement('active.connections', 2)
    """
    _STATSD.decrement(metric, value=value, tags=tags)


def histogram(metric, value, tags=None):
    """
    Sample a histogram value, optionally setting tags and a sample rate.

    >>> histogram('uploaded.file.size', 1445)
    >>> histogram('album.photo.count', 26, tags=["gender:female"])
    """
    _STATSD.histogram(metric, value=value, tags=tags)


def timing(metric, value, tags=None):
    """
    Record a timing, optionally setting tags and a sample rate.

    >>> timing("query.response.time", 1234)
    """
    _STATSD.timing(metric, value=value, tags=tags)
