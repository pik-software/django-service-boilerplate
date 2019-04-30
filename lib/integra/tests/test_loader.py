from lib.integra.utils import Loader


def test_loader_protocol(mocker):
    model = {
        'url': '/api/v1/contact-list/',
        'app': 'housing',
        'model': 'contact'}
    config = {
        'base_url': 'https://housing.pik-software.ru/',
        'request': {},
        'models': [model]}
    result = [{'app': 'housing', 'model': 'contact', 'data': {'_uid': '0'}}]

    loader = Loader(config)
    with mocker.patch.object(loader, '_request', return_value=result):
        downloaded = list(loader.download(model))

        assert downloaded == result
        loader._request.assert_called_once_with(model, None)  # noqa: pylint=protected-access
