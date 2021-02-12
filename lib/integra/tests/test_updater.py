from lib.integra.models import UpdateState
from lib.integra.tests.factories import UpdateStateFactory
from lib.integra.utils import Updater


def test_updater_protocol_create():
    with Updater(app='integra', model_name='updatestate') as updater:
        updater.update({
            '_uid': 'updater1',
            '_type': 'updatestate'
        })

    assert UpdateState.objects.count() == 1
    assert UpdateState.objects.last().key == 'updater1'


def test_updater_update():
    updated_value = '2018-01-12T22:33:45.011349'
    UpdateStateFactory(key='updater1', updated=None)

    with Updater(app='integra', model_name='updatestate') as updater:
        updater.update({
            '_uid': 'updater1',
            '_type': 'updatestate',
            'updated': updated_value,
        })

    assert UpdateState.objects.count() == 2
    assert UpdateState.objects.last().key == 'updater1'
    assert UpdateState.objects.last().updated.isoformat() == updated_value
    assert updater.last_updated == updated_value
