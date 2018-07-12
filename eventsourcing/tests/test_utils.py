from time import time

import pytest
from pik.core.tests import create_user

from ..utils import HistoryObject


@pytest.fixture()
def hist_obj():
    instance = create_user()
    return HistoryObject(
        instance, int(time()), '+',
        str(instance.pk), 'user', 1)


def test_pack_and_unpack(hist_obj: HistoryObject):
    unpacked = HistoryObject.unpack(*hist_obj.pack())
    assert hist_obj.instance == unpacked.instance
    assert hist_obj.instance_uid == unpacked.instance_uid
    assert hist_obj.instance_type == unpacked.instance_type
    assert hist_obj.instance_version == unpacked.instance_version
    assert hist_obj.history_type == unpacked.history_type
    assert hist_obj.history_id == unpacked.history_id


def test_get_event_names(hist_obj: HistoryObject):
    assert hist_obj.get_event_names() == [
        'user', 'user.+', f'user.+.{hist_obj.instance.pk}']


def test_get_event_parts(hist_obj: HistoryObject):
    assert hist_obj.get_event_parts() == (
        'user', '+', f'{hist_obj.instance.pk}')


def test_repr(hist_obj: HistoryObject):
    _uid = hist_obj.instance_uid
    assert repr(hist_obj) == f"<HistoryObject(auth.user.{_uid}, " \
                             f"{hist_obj.history_id}, '+', " \
                             f"'{_uid}', 'user', 1)>"
