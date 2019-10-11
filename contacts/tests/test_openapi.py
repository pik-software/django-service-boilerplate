from rest_framework import status


def test_api_schema_unauthorized(anon_api_client):
    res = anon_api_client.get("/api/v1/schema/")
    assert res.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


def test_api_common_schema(api_client):
    res = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["openapi"] == "3.0.2"
    assert data["info"]["title"] == "Сервис API"
    assert data["info"]["description"] == ("Тестовый сервис. Предоставляет "
                                           "инструменты для управления "
                                           "контактами и комментариями.")


def test_api_schema(api_client):
    response = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert response.status_code == 200
    data = response.json()
    definitions = data["components"]["schemas"]
    assert "Comment" in definitions
    assert "Contact" in definitions
    assert "/api/v1/comment-list/" in data["paths"]
    assert "/api/v1/comment-list/{_uid}/" in data["paths"]
    assert "/api/v1/contact-list/" in data["paths"]
    assert "/api/v1/contact-list/{_uid}/" in data["paths"]


def test_api_contact_model_schema(api_client):
    response = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert response.status_code == 200
    data = response.json()
    contact = data["components"]["schemas"]["Contact"]
    assert contact == {
        "properties": {
            "_uid": {"type": "string", "title": " uid", "readOnly": True},
            "_type": {
                "type": "string",
                "title": " type",
                "readOnly": True,
                "enum": ["contact"],
            },
            "_version": {
                "type": "string",
                "title": " version",
                "readOnly": True,
            },
            "created": {
                "type": "string",
                "format": "date-time",
                "title": "Создан",
                "readOnly": True,
            },
            "updated": {
                "type": "string",
                "format": "date-time",
                "title": "Updated",
                "readOnly": True,
            },
            "name": {
                "type": "string",
                "title": "Наименование",
                "maxLength": 255,
            },
            "phones": {
                "type": "array",
                "items": {"type": "string"},
                "title": "Номера телефонов",
                "description": "Номера телефонов вводятся в произвольном "
                "формате через запятую",
            },
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "title": "E-mail адреса",
                "description": "E-mail адреса вводятся через запятую",
            },
            "order_index": {
                "type": "integer",
                "maximum": 2147483647,
                "minimum": -2147483648,
                "title": "Индекс для сортировки",
            },
        },
        "required": ["name"],
    }


def test_api_contact_schema(api_client):
    response = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert response.status_code == 200
    data = response.json()
    comment = data["paths"]["/api/v1/contact-list/"]["get"]["responses"]
    items = {"anyOf": [{"$ref": "#/components/schemas/Contact"}]}
    assert comment == {
        "200": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "example": 123},
                            "next": {"type": "string", "nullable": True},
                            "previous": {"type": "string", "nullable": True},
                            "results": {
                                "type": "array",
                                "items": items
                            },
                        },
                    }
                }
            },
            "description": "",
        }
    }


def test_api_comment_model_schema(api_client):
    response = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert response.status_code == 200
    data = response.json()
    comment = data["components"]["schemas"]["Comment"]
    assert comment == {
        "properties": {
            "_uid": {"type": "string", "title": " uid", "readOnly": True},
            "_type": {
                "type": "string",
                "title": " type",
                "readOnly": True,
                "enum": ["comment"],
            },
            "_version": {
                "type": "string",
                "title": " version",
                "readOnly": True,
            },
            "created": {
                "type": "string",
                "format": "date-time",
                "title": "Создан",
                "readOnly": True,
            },
            "updated": {
                "type": "string",
                "format": "date-time",
                "title": "Updated",
                "readOnly": True,
            },
            "user": {"type": "integer", "title": "User"},
            "contact": {
                "anyOf": [{"$ref": "#/components/schemas/Contact"}],
                "title": "contact",
                "description": "",
            },
            "message": {"type": "string", "title": "Сообщение"},
        },
        "required": ["contact", "message"],
    }


def test_api_comment_schema(api_client):
    response = api_client.get(f"/api/v1/schema/?format=openapi-json")
    assert response.status_code == 200
    data = response.json()
    comment = data["paths"]["/api/v1/comment-list/"]["get"]["responses"]
    items = {"anyOf": [{"$ref": "#/components/schemas/Comment"}]}
    assert comment == {
        "200": {
            "description": "",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "example": 123},
                            "next": {"type": "string", "nullable": True},
                            "previous": {"type": "string", "nullable": True},
                            "results": {
                                "type": "array",
                                "items": items}}}}}}}
