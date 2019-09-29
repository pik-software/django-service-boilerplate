from celery import shared_task


@shared_task(bind=True)
def debug_task(self):
    return 'Request: {0!r}'.format(self.request.task)


def test_create_task(celery_worker):
    req = debug_task.delay()
    assert req.status in ['PENDING', 'SUCCESS']
    assert req.get() == "Request: '_project_.tests.test_celery.debug_task'"
