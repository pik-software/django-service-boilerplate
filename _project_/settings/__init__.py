# coding=utf-8
# django stub settings file please don`t modify it
# use global_stub_settings.py
from .default_settings import *

# project level settings file for main project settings
from .common_settings import *

# section settings for complex apps
from .sections import update_settings
update_settings(globals())

try:
    # settings for you only, not for team (git ignored!)
    from .local_settings import *
except ImportError:
    try:
        # settings for production env may be auto generated
        from .production_settings import *
    except ImportError:
        pass
