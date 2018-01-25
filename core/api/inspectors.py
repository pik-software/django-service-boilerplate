from rest_framework.metadata import SimpleMetadata
from rest_framework.schemas import AutoSchema


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
