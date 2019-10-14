from .abstract_schema_models import BaseUser
from .abstract_schema_models import BaseHistoricalContact
from .abstract_schema_models import BaseContact
from .abstract_schema_models import BaseHistoricalComment
from .abstract_schema_models import BaseComment


class User(BaseUser):
    pass


class HistoricalContact(BaseHistoricalContact):
    pass


class Contact(BaseContact):
    pass


class HistoricalComment(BaseHistoricalComment):
    pass


class Comment(BaseComment):
    pass


