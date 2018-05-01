from django.utils.crypto import get_random_string

from core.tasks.fixtures import create_user
from eventsourcing.consts import WEBHOOK_SUBSCRIPTION
from ..models import subscribe, unsubscribe


def _assert_subscription(subscription, user, name, type, settings, events):
    assert subscription.user == user
    assert subscription.name == name
    assert subscription.type == type
    assert subscription.settings == settings
    assert subscription.events == events


def test_subscribe():
    user = create_user()
    name = get_random_string()
    subscription = subscribe(user, name, WEBHOOK_SUBSCRIPTION, {}, [name])
    _assert_subscription(
        subscription, user, name, WEBHOOK_SUBSCRIPTION, {}, [name])


def test_double_subscribe():
    user = create_user()
    name = get_random_string()
    subscribe(user, name, WEBHOOK_SUBSCRIPTION, {}, [name])
    subscription = subscribe(user, name, WEBHOOK_SUBSCRIPTION, {}, [name])
    _assert_subscription(
        subscription, user, name, WEBHOOK_SUBSCRIPTION, {}, [name])


def test_subscribe_different_events():
    user = create_user()
    name1, name2 = get_random_string(), get_random_string()
    subscribe(user, name1, WEBHOOK_SUBSCRIPTION, {}, [name1])
    subscription = subscribe(user, name1, WEBHOOK_SUBSCRIPTION, {}, [name2])
    _assert_subscription(
        subscription, user, name1, WEBHOOK_SUBSCRIPTION, {}, [name1, name2])


def test_unsubscribe():
    user = create_user()
    name = get_random_string()
    subscribe(user, name, WEBHOOK_SUBSCRIPTION, {}, [name])
    subscription = unsubscribe(user, name, WEBHOOK_SUBSCRIPTION, [name])
    _assert_subscription(
        subscription, user, name, WEBHOOK_SUBSCRIPTION, {}, [])


def test_unsubscribe_without_subscription():
    user = create_user()
    name = get_random_string()
    subscription = unsubscribe(user, name, WEBHOOK_SUBSCRIPTION, [name])
    _assert_subscription(
        subscription, user, name, WEBHOOK_SUBSCRIPTION, {}, [])
