from django.utils.crypto import get_random_string
from django.utils.timezone import now

from lib.integra.models import UpdateState


def test_interface():
    type_name = get_random_string()
    now_time = now()

    date_time = UpdateState.objects.get_last_updated(type_name)
    assert date_time is None

    date_time = UpdateState.objects.get_last_updated(type_name)
    assert date_time is None

    UpdateState.objects.set_last_updated(type_name, now_time)

    date_time = UpdateState.objects.get_last_updated(type_name)
    assert date_time == now_time

    date_time = UpdateState.objects.get_last_updated(type_name)
    assert date_time == now_time
