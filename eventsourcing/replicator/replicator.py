from django.conf import settings as dj_settings

from .registry import _to_hist_obj, get_all_replicating_models
from .serializer import _check_serialize_problem
from ..consts import WEBHOOK_SUBSCRIPTION
from ..models import Subscription
from ..utils import HistoryObject, ReplicatorSerializeError

_LATEST_API_VERSION_SETTING = 'REST_FRAMEWORK_LATEST_API_VERSION'


def _replicate(hist_obj: HistoryObject, subscription=None) -> None:
    from .tasks import _replicate_to_webhook_subscribers  # noqa
    from .tasks import _process_webhook_subscription  # noqa

    packed_hist_obj = hist_obj.pack()
    if subscription:
        _process_webhook_subscription.apply_async(
            args=(subscription.pk, packed_hist_obj,), countdown=0.5,
        )
    else:
        _replicate_to_webhook_subscribers.apply_async(
            args=(packed_hist_obj, ), countdown=0.5)


def _re_replicate(subscription, events):
    from .tasks import _re_replicate_webhook_subscription  # noqa

    _re_replicate_webhook_subscription.apply_async(
        args=(subscription.pk, events), countdown=0.5)


def _get_subscription_statuses(user, settings=None):
    if not settings:
        version = getattr(dj_settings, _LATEST_API_VERSION_SETTING, '1')
        settings = {'api_version': version}

    result = {}
    for _type, model in get_all_replicating_models():
        try:
            result[_type] = 'OK'
            _check_serialize_problem(user, settings, _type)
            last_obj = model.objects.last()
            if last_obj:
                subscription = Subscription(
                    user=user,
                    name='fake', type=WEBHOOK_SUBSCRIPTION,
                    settings=settings, events=[_type])
                hist_obj = _to_hist_obj(last_obj)
                hist_obj.serialize(subscription)
        except ReplicatorSerializeError as exc:
            result[_type] = f'ERROR: {exc}'
    return result
