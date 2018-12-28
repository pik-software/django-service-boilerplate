from _project_.celery import debug_task


def test_create_task(celery_session_worker):
    celery_session_worker.app.control.purge()  # clear all existed tasks
    req = debug_task.delay()
    assert req.status in ['PENDING', 'SUCCESS']
    assert req.get(timeout=10) == "Request: '_project_.celery.debug_task'"
