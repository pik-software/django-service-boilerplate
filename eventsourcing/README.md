This module represent described by Martin Fowler "Event-Carried State Transfer"
You can read more detail in article ["What do you mean by “Event-Driven”?"][1].

Let's see how to use the `eventsourcing`.

1) We have a model `Contract` and we want to have this model
in a different services. It means we want to have `replicating` model
to replicate this model to others services.

`master-service`:

```python

    from pik.core.models import BasePHistorical
    from eventsourcing.replicator import replicating

    @replicating('contract')
    class Contract(BasePHistorical):
        number = models.CharField(max_length=255)
        ...

```

2) We want to create a model `ContractReplica` in a service when
you create the `Contract` in master service. It means we want
to have `replicated` model in other service.

`replica-service`:

```python

    from pik.core.models import BasePHistorical
    from eventsourcing.replicated import replicated

    @replicated('contract')
    class ContractReplica(BasePHistorical):
        number = models.CharField(max_length=255)
        ...

```

3) You should know protocol between master and replica.
The communication is realized through the mechanism of webhook
callbacks. Each object state change creates a historical
Create/Update/Delete event log. This event log is distributed to all
subscribers via webhook callbacks. Example of "created event" for
`Contract` model.

```json
{
    "count": 1,
    "results": [
        {
            "history_id": 133,
            "history_date": "2018-04-30T12:04:33.690145",
            "history_change_reason": null,
            "history_user_id": null,
            "history_type": "+",
            "_uid": "123e4567-e89b-12d3-a456-426655440000",
            "_type": "contract",
            "_version": 1,
            "number": "N14/10-11",
            ...
        }
    ]
}
```

Each models (`replicating`/`replicated`) must have `uid` and `version`
fields. These fields are required to correctly restore the state
change sequence.

Each historical event record has:
 - 5 history service fields: `history_id`, `history_date`,
   `history_change_reason`, `history_user_id`, `history_type`
 - 3 entity service fields: `_uid`, `_type`, `_version`

4) Replica-service should subscribe on Create/Update/Delete events.

5) Master-service should send events to all subscribers.

```python
from rest_framework.routers import DefaultRouter

from eventsourcing.replicated import WebhookCallbackViewSet
from eventsourcing.replicator import SubscriptionViewSet

webhook = DefaultRouter()
webhook.register(
    'callback', WebhookCallbackViewSet, base_name='callback')
webhook.register(
    'subscriptions', SubscriptionViewSet, base_name='subscription')

urlpatterns = [
    ...
    url(r'^api/v(?P<version>[1-9])/', include(webhook.urls)),
]
```

Use `/api/v1/subscriptions` to subscribe on events.

# History object lifecycle #

 1. Each `@replicating(Model)` has `post_delete`, `post_save` signal listeners
 2. Signal listener create `hist_obj = HistoryObject(instance, ...)`
 3. Signal listener run `hist_obj.replicate()`
 4. `HistoryObject.replicate()` create async Celery task
 5. Async task run `serialized_data = hist_obj.serialize(subscription)`
 6. Async task run `hist_obj.delivery(subscription, serialized_data)`

[1]: https://martinfowler.com/articles/201701-event-driven.html
