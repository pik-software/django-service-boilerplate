import os
from contextlib import contextmanager

import pytest
from django import setup as django_setup
from django.core.cache import caches
from django.test import TransactionTestCase
from selenium import webdriver

from _project_ import celery_app as django_celery_app


# Transaction rollback emulation
# http://docs.djangoproject.com/en/2.0/topics/testing/overview/#rollback-emulation
TransactionTestCase.serialized_rollback = True


@pytest.fixture()
def anon_api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def api_user():
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    user = user_model(username='test', email='test@test.ru', is_active=True)
    user.set_password('test_password')
    user.save()
    return user


@pytest.fixture
def api_client(api_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_login(api_user)
    return client


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
    django_setup()


@pytest.fixture(scope='session')
def base_url(live_server):
    return live_server.url


@pytest.fixture(autouse=True)
def clear_caches():
    for cache in caches.all():
        cache.clear()


# CELERY

@pytest.fixture(scope='session')
def celery_session_app(request):
    """Session Fixture: Return app for session fixtures."""
    yield django_celery_app


# CELENIUM

@pytest.fixture
def driver_class(request):
    return webdriver.PhantomJS


@pytest.fixture
def driver_kwargs():
    return {}


@pytest.yield_fixture
def driver(request, driver_class, driver_kwargs):
    """Returns a WebDriver instance based on options and capabilities"""
    driver_instance = driver_class(**driver_kwargs)
    yield driver_instance
    driver_instance.quit()


@pytest.fixture(scope='function', autouse=True)
def _skip_sensitive(request):
    """Pytest-selenium patch: don't Skip destructive tests"""


def pytest_addoption(parser):
    parser.addoption(
        "--selenium", action="store_true", default=False,
        help="run selenium marked tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--selenium"):
        # if --selenium given in cli: do not skip the selenium tests
        return
    skip_selenium = pytest.mark.skip(reason="need --selenium option to run")
    for item in items:
        if "selenium" in item.keywords:
            item.add_marker(skip_selenium)


# HELPERS

@pytest.fixture(scope='function')
def assert_num_queries_lte(pytestconfig):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    @contextmanager
    def _assert_num_queries(num):
        with CaptureQueriesContext(connection) as context:
            yield
            queries = len(context)
            if queries > num:
                msg = f"Expected to perform less then {num} queries" \
                      f" but {queries} were done"
                if pytestconfig.getoption('verbose') > 0:
                    sqls = (q['sql'] for q in context.captured_queries)
                    msg += '\n\nQueries:\n========\n\n%s' % '\n\n'.join(sqls)
                else:
                    msg += " (add -v option to show queries)"
                pytest.fail(msg)

    return _assert_num_queries
