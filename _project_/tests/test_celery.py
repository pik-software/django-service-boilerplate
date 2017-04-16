from _project_.celery import debug_task, app


def test_create_task(celery_session_worker):
    x = debug_task.delay()
    assert x.status in ['PENDING', 'SUCCESS']
    assert x.get(timeout=10) == "Request: '_project_.celery.debug_task'"
