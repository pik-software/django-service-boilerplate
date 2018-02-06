import os

from selenium import webdriver
import pytest
import django
from celery.contrib.testing import worker, tasks  # noqa: pylint=unused-import

from _project_ import celery_app as django_celery_app


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project_.settings")
    django.setup()


@pytest.fixture(scope='session')
def base_url(live_server):
    return live_server.url


# CELERY

@pytest.fixture(scope='session')
def celery_session_app(request):
    """Session Fixture: Return app for session fixtures."""
    yield django_celery_app


@pytest.fixture(scope='session')
def celery_session_worker(request,
                          celery_session_app,  # noqa: pylint=redefined-outer-name
                          celery_worker_pool,
                          celery_worker_parameters):
    """Session Fixture: Start worker that lives throughout test suite."""
    with worker.start_worker(celery_session_app,
                             pool=celery_worker_pool,
                             **celery_worker_parameters) as worker_context:
        yield worker_context


# CELENIUM

@pytest.fixture
def driver_class(request):
    return webdriver.PhantomJS


@pytest.fixture
def driver_kwargs():
    return {}


@pytest.yield_fixture
def driver(request, driver_class, driver_kwargs):  # noqa: pylint=redefined-outer-name
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
