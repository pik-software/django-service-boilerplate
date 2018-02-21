from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string


def test_create_new_file():
    data = get_random_string().encode()
    path = default_storage.save('test1/test.txt', ContentFile(data))
    assert default_storage.open(path).read() == data
