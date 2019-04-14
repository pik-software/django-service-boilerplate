from lib.integra.models import UpdateState
from lib.integra.utils import Updater


def test_updater_protocol_create():
    updater = Updater()
    count = UpdateState.objects.count()

    updater.update({
        'app': 'integra',
        'model': 'updatestate',
        'data': {'_uid': 'updater1', '_type': 'updatestate'},
    })

    assert UpdateState.objects.count() == count + 1
    assert UpdateState.objects.last().key == 'updater1'


def test_updater_protocol_update():
    updater = Updater()
    count = UpdateState.objects.count()
    updated_value = '2018-01-12T22:33:45.011349'

    updater.update({
        'app': 'integra',
        'model': 'updatestate',
        'data': {'_uid': 'updater1', '_type': 'updatestate',
                 'updated': '2012-04-12T22:33:45.028342'},
    })
    updater.update({
        'app': 'integra',
        'model': 'updatestate',
        'data': {'_uid': 'updater1', '_type': 'updatestate',
                 'updated': updated_value},
    })

    assert UpdateState.objects.count() == count + 1
    assert UpdateState.objects.last().key == 'updater1'
    assert UpdateState.objects.last().updated.isoformat() == updated_value
