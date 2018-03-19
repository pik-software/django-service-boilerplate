from _project_.celery import debug_task, app  # noqa: pylint=unused-import


def test_create_task(celery_session_worker):
    x = debug_task.delay()  # noqa: pylint=invalid-name
    assert x.status in ['PENDING', 'SUCCESS']
    assert x.get(timeout=10) == "Request: '_project_.celery.debug_task'"
