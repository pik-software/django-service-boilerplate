import pytest
from rest_framework.test import APIClient

from core.tasks.fixtures import create_user
from eventsourcing.replicator.registry import check_all_models_replicating


@pytest.fixture
def api_client():
    user = create_user()
    client = APIClient()
    client.force_login(user)
    client.user = user
    return client


def test_check_replicating_models(api_client):
    result = check_all_models_replicating(api_client.user)
    assert result == {
        'comment': 'ERROR: serialize api status = 403',
        'contact': 'ERROR: serialize api status = 403',
    }
