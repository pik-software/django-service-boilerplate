from copy import deepcopy
from unittest import mock

from lib.integra.tasks import Integra
from ..models import Contact

RESULT = [
    {
        "_uid": "07326036-9baf-41cb-91fc-1d2f702fdec9",
        "_type": "contact",
        "_version": 5,
        "created": "2018-02-17T22:02:57.666548",
        "updated": "2019-04-07T10:49:17.500849",
        "name": "Steven Carrol9l",
        "phones": [
            "5203"
        ],
        "emails": [
            "steven carroll@example.com"
        ],
        "order_index": 10089
    },
    {
        "_uid": "07326036-9baf-41cb-91fc-1d2f702fdec9",
        "_type": "contact",
        "_version": 6,
        "created": "2018-02-17T22:02:57.666548",
        "updated": "2019-04-07T10:49:27.494178",
        "name": "Carla 2",
        "phones": [
            "2386"
        ],
        "emails": [
            "carla maddox@example.com"
        ],
        "order_index": 1009
    },
    {
        "_uid": "07326036-9baf-41cb-91fc-1d2f702fdec9",
        "_type": "contact",
        "_version": 13,
        "created": "2018-02-17T22:02:57.666548",
        "updated": "2019-04-07T10:50:58.897061",
        "name": "d",
        "phones": [
            "8500"
        ],
        "emails": [
            "wayne brown@example.com"
        ],
        "order_index": 100
    },
    {
        "_uid": "0168245f-0298-4048-5f26-a108fed49d92",
        "_type": "contact",
        "_version": 15,
        "created": "2019-01-06T18:13:52.922085",
        "updated": "2019-04-07T10:51:23.401410",
        "name": "lklklk",
        "phones": [
            "9989"
        ],
        "emails": [
            "it-services@pik-comfort.ru",
            "qwe@qwe.q9j2"
        ],
        "order_index": 100
    },
    {
        "_uid": "12134bdd-d71b-4731-b72a-c16c9cf9b587",
        "_type": "contact",
        "_version": 6,
        "created": "2018-02-17T22:02:57.609496",
        "updated": "2019-04-07T10:53:16.349032",
        "name": "Angela 3f",
        "phones": [
            "2583"
        ],
        "emails": [
            "angela rogers@example.com"
        ],
        "order_index": 10021
    },
    {
        "_uid": "12134bdd-d71b-4731-b72a-c16c9cf9b587",
        "_type": "contact",
        "_version": 32,
        "created": "2018-02-17T22:02:57.609496",
        "updated": "2019-04-07T10:57:37.778117",
        "name": "Jonathan Sheppard",
        "phones": [
            "2021"
        ],
        "emails": [
            "jonathan sheppard@example.com"
        ],
        "order_index": 1001
    },
    {
        "_uid": "0f273e43-a8cc-471e-bc6f-a66479c9f340",
        "_type": "contact",
        "_version": 4,
        "created": "2018-02-17T22:02:52.142320",
        "updated": "2019-04-07T12:06:56.221892",
        "name": "Suzanne 2",
        "phones": [
            "7221"
        ],
        "emails": [
            "suzanne nichols@example.com"
        ],
        "order_index": 120
    },
    {
        "_uid": "710c2484-baba-4d10-9972-61dfeca58237",
        "_type": "contact",
        "_version": 5,
        "created": "2018-02-17T22:02:46.549939",
        "updated": "2019-04-07T12:07:23.345818",
        "name": "David 3",
        "phones": [
            "3930"
        ],
        "emails": [
            "david huber@example.com"
        ],
        "order_index": 10
    },
    {
        "_uid": "12134bdd-d71b-4731-b72a-c16c9cf9b587",
        "_type": "contact",
        "_version": 44,
        "created": "2018-02-17T22:02:57.609496",
        "updated": "2019-04-07T12:09:37.690856",
        "name": "eee 2",
        "phones": [
            "4382"
        ],
        "emails": [
            "richard nielsen@example.com"
        ],
        "order_index": 100
    },
    {
        "_uid": "bd915ab7-fe7e-49db-bd06-890a292ba609",
        "_type": "contact",
        "_version": 4,
        "created": "2018-02-17T22:02:57.602702",
        "updated": "2019-04-07T12:09:49.146435",
        "name": "q",
        "phones": [
            "9663"
        ],
        "emails": [
            "craig bennett@example.com"
        ],
        "order_index": 1002
    },
    {
        "_uid": "6cb6eece-fd33-4753-8aad-10fcec366a61",
        "_type": "contact",
        "_version": 6,
        "created": "2018-02-17T22:02:57.642757",
        "updated": "2019-04-07T13:05:15.727494",
        "name": "e",
        "phones": [
            "5827"
        ],
        "emails": [
            "linda johnson@example.com"
        ],
        "order_index": 1002
    },
    {
        "_uid": "8df69d66-803e-48f3-b16f-545ee63c9dba",
        "_type": "contact",
        "_version": 12,
        "created": "2018-02-17T22:02:57.632498",
        "updated": "2019-04-07T13:13:41.236663",
        "name": "awdawd",
        "phones": [
            "9685"
        ],
        "emails": [
            "amyedwards@example.com"
        ],
        "order_index": 100
    },
    {
        "_uid": "0168244e-78dd-ed03-f5d9-acc5b69fdd60",
        "_type": "contact",
        "_version": 21,
        "created": "2019-01-06T17:55:49.086308",
        "updated": "2019-04-07T13:24:46.201704",
        "name": "2eee",
        "phones": [],
        "emails": [
            "it-services@pik-comfort.ru49"
        ],
        "order_index": 102222223
    },
    {
        "_uid": "0168243a-7048-de6f-20da-7f222a7f1087",
        "_type": "contact",
        "_version": 9,
        "created": "2019-01-06T17:33:56.387480",
        "updated": "2019-04-07T13:26:38.702762",
        "name": "022awdawd",
        "phones": [],
        "emails": [
            "it-services@pik-comfort.rx"
        ],
        "order_index": 1001
    },
    {
        "_uid": "0168243a-7048-de6f-20da-7f222a7f1087",
        "_type": "contact",
        "_version": 2,
        "created": "2019-04-14T23:09:47.202970",
        "updated": "2019-04-14T23:09:57.585576",
        "name": "new-one!",
        "phones": [],
        "emails": [],
        "order_index": 100
    },
]


def _make_integra():
    return Integra({
        'base_url': 'http://127.0.0.1:8000',
        'request': {'auth': 'api-reader:MyPass39dza2es'},
        'models': [
            {'url': '/api/v1/contact-list/',
             'app': 'contacts',
             'model': 'contact'},
        ]})


@mock.patch('lib.integra.utils._fetch_data_from_api')
def test_integra_run(fetch):
    fetch.return_value = deepcopy(RESULT)
    integra = _make_integra()
    processed = integra.run()

    fetch.assert_called_once_with(
        'http://127.0.0.1:8000/api/v1/contact-list/',
        ('api-reader', 'MyPass39dza2es'),
        {'ordering': 'updated'})
    assert Contact.objects.count() == 10
    assert processed == 15

    obj = Contact.objects.get(uid='0168243a-7048-de6f-20da-7f222a7f1087')
    assert obj.version == 9
    assert obj.name == '022awdawd'


@mock.patch('lib.integra.utils._fetch_data_from_api')
def test_integra_run_on_the_same_result(fetch):
    integra = _make_integra()
    fetch.return_value = deepcopy(RESULT)
    integra.run()
    fetch.return_value = deepcopy(RESULT)
    processed = integra.run()
    assert processed == 15


@mock.patch('lib.integra.utils._fetch_data_from_api')
def test_integra_update(fetch):
    fetch.return_value = deepcopy(RESULT)
    integra = _make_integra()
    integra.run()
    fetch.return_value = [
        {
            "_uid": "0168243a-7048-de6f-20da-7f222a7f1087",
            "_type": "contact",
            "_version": 10,
            "created": "2019-04-14T23:09:47.202970",
            "updated": "2020-06-14T23:09:57.585576",
            "name": "new-one! (up)",
            "phones": [],
            "emails": [],
            "order_index": 100
        },
    ]

    processed = integra.run()
    assert processed == 1
