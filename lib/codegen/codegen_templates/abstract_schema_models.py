from django.contrib.postgres.fields import JSONField
from django.db import models


{% for name, definition in schema.definitions.items() %}
class Base{{name}}(models.Model):
    {% for prop_name, property in definition.properties.items() | skip_items_keys(['_type']) %}
    {{ prop_name|to_model_field_name }} = {{ property|to_model_field(prop_name) }}
    {% endfor %}

    class Meta:
        abstract = True


{% endfor %}