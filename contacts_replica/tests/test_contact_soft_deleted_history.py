# pylint: disable=protected-access
from ..tests.factories import ContactReplicaFactory, \
    CommentReplicaFactory


def _assert_history_object(hist_obj, type_, event_, uid_):
    _type = hist_obj.history_object._meta.model_name
    _event = hist_obj.history_type
    _uid = hist_obj.history_object.uid
    assert _type == type_
    assert _event == event_
    assert _uid == uid_


def test_soft_delete_obj():
    contact = ContactReplicaFactory.create()
    comment = CommentReplicaFactory.create(contact=contact)
    contact_hist = contact.history.all()
    comment_hist = comment.history.all()

    contact.delete()

    assert contact_hist.count() == 2
    assert comment_hist.count() == 2
    _assert_history_object(comment_hist[0], 'commentreplica', '-', comment.uid)
    _assert_history_object(comment_hist[1], 'commentreplica', '+', comment.uid)
    _assert_history_object(contact_hist[0], 'contactreplica', '-', contact.uid)
    _assert_history_object(contact_hist[1], 'contactreplica', '+', contact.uid)
