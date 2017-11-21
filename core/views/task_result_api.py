import json

from celery.result import AsyncResult
from django.http import JsonResponse


def task_result_api_view(request, taskid):
    """
    Get task `state` and `result` from API endpoint.

    Use case: you want to provide to some user with async feedback about
    about status of some task.

    Example:

        # urls.py
        urlpatterns = [
            url(r'^api/task/result/(.+)/', task_result_api_view),
            ...
        ]

        # some_views.py
        context = {}
        # ...
        async_request = some_important_task.delay(...)
        # ...
        context['async_task_id'] = str(async_request.id)

    Now we can check the state and result form Front-end side.
    """
    result = AsyncResult(taskid)
    response = {'task-id': taskid, 'state': result.state}
    response.update({'result': _safe_result(result.result)})
    return JsonResponse(response)


def _safe_result(result):
    """returns json encodable result"""
    try:
        json.dumps(result)
    except TypeError:
        return repr(result)
    else:
        return result
