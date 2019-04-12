{% for name, definition in schema.definitions.items() %}
from .abstract_schema_models import Base{{name}}
{% endfor %}


{% for name, definition in schema.definitions.items() %}
class {{name}}(Base{{name}}):
    pass


{% endfor %}