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
    assert hist_obj._uid == unpacked._uid
    assert hist_obj._type == unpacked._type
    assert hist_obj._version == unpacked._version
    assert hist_obj.history_type == unpacked.history_type
    assert hist_obj.history_id == unpacked.history_id


def test_get_event_names(hist_obj: HistoryObject):
    assert hist_obj.get_event_names() == [
        'user', 'user.+', f'user.+.{hist_obj.instance.pk}']


def test_get_event_parts(hist_obj: HistoryObject):
    assert hist_obj.get_event_parts() == (
        'user', '+', f'{hist_obj.instance.pk}')


def test_repr(hist_obj: HistoryObject):
    assert repr(hist_obj) == f"<HistoryObject(auth.user.{hist_obj._uid}, " \
                             f"{hist_obj.history_id}, '+', " \
                             f"'{hist_obj._uid}', 'user', 1)>"
