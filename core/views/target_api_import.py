import os
import logging
from time import time

from django.conf import settings
from django.core.files.storage import default_storage

from rest_framework.decorators import (
    api_view, parser_classes, permission_classes)
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from core.tasks.target_api_import import import_from_file
from core.api.permissions import APIImport


LOGGER = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([APIImport])
@parser_classes([MultiPartParser])
def async_file_import_view(request):
    """ Save file to __data__/media/<service_name/> and run celery task.
        If success return 204 and task_id. """
    file_ = request.data.get('data.txt')

    if file_ is None:
        return Response(status=400)

    base_dir = f'{settings.MEDIA_ROOT}/{settings.SERVICE_TITLE}'
    filename = f'import_{time()}.txt'
    save_dir = os.path.join(base_dir, filename)
    saved_file = default_storage.save(save_dir, file_)
    result = import_from_file.delay(saved_file)
    return Response({'task-id': result.task_id})
