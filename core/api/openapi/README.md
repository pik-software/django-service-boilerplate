---------
OpenAPI 3
---------

Features
---------

- Schema version fetching from `RELEASE` env variable.
- Schema title generation as `f'{settings.SERVICE_TITLE} API'`.
- Components schemas generation from ModelSerializers.
- Schema description fetching from `settings.DERVICE_DESCRIPTION`
- `enumNames` generation from choices human readable names. 
- `SerializerMethodField` type hint introspection.

Schema Customization
--------------------

Serializer schema customization
-------------------------------

Inject schema customization, through `update_schema` dict:

```python
class MySerializer(ModelSerializer):
    update_schema = {
        'properties': {
            'uid': {'deprecated': True}
        }
    }
```

Inject schema customization, though `update_schema` callback:

```python
class MySerializer(ModelSerializer):
    def update_schema(self, schema):
        schema['properties']['_uid']['deprecated'] = True
        return schema
```

ViwSet Schema customization
------------------------

Inject schema customization, through `update_schema` dict:

```python
class MyViewSet(ViewSet):
    update_schema = {
        '/api/v1/comment-list/': {
            'get': {
                'deprecated': True,
            }
        }
    }
```
Inject schema customization, though `update_schema` callback:

```python
class MyViewSet(ViewSet):
    def update_schema(self, schema):
        schema['/api/v1/comment-list/']['get']['deprecated'] = True
        return schema
```