from unittest.mock import MagicMock

import pytest
from django.db import models
from django.test import override_settings
from rest_framework.exceptions import NotFound, ValidationError

from core.api.mixins.history import HistoryQueryParamsValidator


NOT_VALID_CURSOR = 'cj0xJnTlkOTAtZjNlY2U5NjZmOTNi'
VALID_CURSOR = 'cj0xJnA9Zjk4NzAyOWEtN2E4ZS00ZDRkLTlkOTAtZjNlY2U5NjZmOTNi'


def test_lookup_field():
    lookup_field = 'url'
    lookup_url_kwarg = '_url'
    lookup_value = 'test'
    query_params = {lookup_url_kwarg: lookup_value}
    validator = HistoryQueryParamsValidator(
        query_params, '_url', lookup_field, ())

    assert lookup_url_kwarg not in validator.query_params
    assert lookup_field in validator.query_params
    assert lookup_value == validator.query_params[lookup_field]


def test_valid_cursor():
    query_params = {'cursor': VALID_CURSOR}
    paginator_field = MagicMock()
    validator = HistoryQueryParamsValidator(
        query_params, None, None, paginator_field)
    validator.validate_query_params()

    assert paginator_field.to_python.called


def test_not_valid_cursor():
    query_params = {'cursor': NOT_VALID_CURSOR}
    validator = HistoryQueryParamsValidator(
        query_params, None, None, MagicMock())

    with pytest.raises(NotFound):
        validator.validate_query_params()


def test_not_valid_value_in_cursor():
    query_params = {'cursor': VALID_CURSOR}
    validator = HistoryQueryParamsValidator(
        query_params, None, None, models.IntegerField())

    with pytest.raises(NotFound):
        validator.validate_query_params()


@override_settings(ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE=1)
def test_allowed_history_date_range():
    query_params = {
        'cursor': VALID_CURSOR,
        'history_date__lt': '2018-09-03T13:37:49.886360',
        'history_date__gte': '2018-09-02T22:37:49.886360',
        'only_last_version': True}
    paginator_field = MagicMock()
    validator = HistoryQueryParamsValidator(
        query_params, None, None, paginator_field)
    validator.validate_query_params()


@override_settings(ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE=1)
def test_not_allowed_history_date_range(): # noqa: pylint=invalid-name
    query_params = {
        'cursor': VALID_CURSOR,
        'history_date__lte': '2018-09-03T13:37:49.886360',
        'history_date__gt': '2018-09-02T12:37:49.886360',
        'only_last_version': True}
    paginator_field = MagicMock()
    validator = HistoryQueryParamsValidator(
        query_params, None, None, paginator_field)

    with pytest.raises(ValidationError):
        validator.validate_query_params()


@override_settings(ONLY_LAST_VERSION_ALLOWED_DAYS_RANGE=1)
def test_without_history_date_range():
    query_params = {'only_last_version': True}
    paginator_field = MagicMock()
    validator = HistoryQueryParamsValidator(
        query_params, None, None, paginator_field)

    with pytest.raises(ValidationError):
        validator.validate_query_params()


def test_history_date_range():
    query_params = {
        'history_date__lt': '2018-09-03T13:37:49.886360',
        'history_date__gt': '2018-09-02T12:37:49.886360'}
    paginator_field = MagicMock()
    validator = HistoryQueryParamsValidator(
        query_params, None, None, paginator_field)

    validator.validate_query_params()
