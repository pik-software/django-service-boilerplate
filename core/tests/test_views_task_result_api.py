import json

from celery import shared_task

from core.views import task_result_api_view


@shared_task(bind=True)
def _task1(self):
    return 'Request: {0!r}'.format(self.request.task)


@shared_task(bind=True)
def _task2(self):
    raise RuntimeError('Request: {0!r}'.format(self.request.task))


def test_get_task_result_task_success(rf, celery_session_worker):
    request = rf.get('/test/')
    task = _task1.delay()

    response = task_result_api_view(request, task.id)
    response = json.loads(response.content.decode('utf-8'))
    assert response == {
        'result': None, 'state': 'PENDING', 'task-id': task.id
    }

    task.get()

    response = task_result_api_view(request, task.id)
    response = json.loads(response.content.decode('utf-8'))
    assert response == {
        'state': 'SUCCESS', 'task-id': task.id,
        'result': "Request: 'core.tests.test_views_task_result_api._task1'",
    }


def test_get_task_result_task_failure(rf, celery_session_worker):
    request = rf.get('/test/')
    task = _task2.delay()

    response = task_result_api_view(request, task.id)
    response = json.loads(response.content.decode('utf-8'))
    assert response == {
        'result': None, 'state': 'PENDING', 'task-id': task.id
    }

    task.get(propagate=False)

    response = task_result_api_view(request, task.id)
    response = json.loads(response.content.decode('utf-8'))
    assert response == {
        'state': 'FAILURE', 'task-id': task.id,
        'result': 'RuntimeError("Request: \''
                  'core.tests.test_views_task_result_api._task2\'",)',
    }
