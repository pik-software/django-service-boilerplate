# coding=utf-8
import os
from os.path import abspath, dirname, join
import sys

__author__ = 'pahaz'
_helpers_dir = abspath(dirname(__file__))
_root_dir = abspath(dirname(dirname(__file__)))

sys.path = [_helpers_dir, _root_dir] + sys.path[:]
os.chdir(_root_dir)


def root_join(*args):
    if not _root_dir:
        raise RuntimeError("Root dir not set. Please use set_root_dir().")
    return join(_root_dir, *args)


from lib2 import conf_from_pyfile

_PROJECT_STUB_SETTINGS_ = root_join("_project_", "stub_settings.py")
settings = conf_from_pyfile(_PROJECT_STUB_SETTINGS_)
