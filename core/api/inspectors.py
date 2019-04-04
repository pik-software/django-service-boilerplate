from deprecated import deprecated
from rest_framework.metadata import SimpleMetadata
from rest_framework.schemas import AutoSchema


@deprecated
class StandardizedAutoSchema(AutoSchema):
    """
    Add this to `settings.py`:

        REST_FRAMEWORK = {
            ...
            'DEFAULT_SCHEMA_CLASS':
                'core.api.inspectors.StandardizedAutoSchema',
            ...
        }

    """


@deprecated
class StandardizedMetadata(SimpleMetadata):
    """
    Add this to `settings.py`:

        REST_FRAMEWORK = {
            ...
            'DEFAULT_METADATA_CLASS':
                'core.api.inspectors.StandardizedMetadata',
            ...
        }

    """
