from lib.integra.utils import Loader


def test_loader_protocol(mocker):
    config = {
        'base_url': 'https://housing.pik-software.ru/',
        'request': {},
        'models': [{
            'url': '/api/v1/contact-list/',
            'app': 'housing',
            'model': 'contact'}]}
    result = [{'app': 'housing', 'model': 'contact', 'data': {'_uid': '0'}}]

    loader = Loader(config)
    with mocker.patch.object(loader, '_request', return_value=result):
        downloaded = list(loader.download())

        assert downloaded == result
        loader._request.assert_called_once_with(config['models'][0], None)  # noqa: pylint=protected-access
