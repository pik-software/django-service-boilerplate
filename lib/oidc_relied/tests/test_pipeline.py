import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


from lib.oidc_relied.pipeline import actualize_roles


@pytest.fixture
def user():
    return get_user_model().objects.create(username="testuser")


def test_actualize_roles_system(user):
    group = Group.objects.create(name='sys-group')
    group.user_set.add(user)

    actualize_roles(user=user, response={'access_token': 'access_token'})

    assert (set(user.groups.values_list('name', flat=True)) ==
            {'sys-group', 'default'})


def test_actualize_roles_extra(user):
    actualize_roles(user=user, response={'access_token': 'access_token',
                                         'roles': [{'name': 'extra'}]})

    assert (set(user.groups.values_list('name', flat=True)) ==
            {'default', 'extra'})


def test_actualize_roles_redundant(user):
    group = Group.objects.create(name='redundant')
    group.user_set.add(user)

    actualize_roles(user=user, response={'access_token': 'access_token'})

    assert set(user.groups.values_list('name', flat=True)) == {'default'}
