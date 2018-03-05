import io
import logging

from django.core.files.storage import default_storage

from celery import app

try:
    from importer import load_for_target
except ImportError as ex:
    logging.warning(f'Unable to import load_for_target!')


@app.shared_task()
def import_from_file(file_name):
    with default_storage.open(file_name) as file_:
        reader = io.BufferedReader(io.BytesIO(file_.read()))
        lines = io.TextIOWrapper(reader, encoding='utf-8')
        load_for_target(lines)
