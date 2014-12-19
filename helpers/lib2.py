# coding=utf-8
import errno
import sys

_py2 = sys.version_info[0] == 2
if _py2:
    string_types = (str, unicode)
else:
    string_types = (str, )


class Config(object):
    pass


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # XXX: py3 review needed
    assert isinstance(import_name, string_types)
    # force the import name to automatically convert to strings
    import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if _py2 and isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError as e:
        if not silent:
            raise


def conf_from_object(obj, silent=False):
    """Return the values from the given object. An object can be of one
    of the following two types:

    -   a string: in this case the object with that name will be imported
    -   an actual object reference: that object is used directly

    Objects are usually either modules or classes.

    Just the uppercase variables in that object are stored in the config.
    Example usage::

        conf_from_object('yourapplication.default_config')
        from yourapplication import default_config
        conf_from_object(default_config)

    """
    if isinstance(obj, string_types):
        obj = import_string(obj, silent=silent)

    if isinstance(obj, dict):
        keys = obj.keys()
        keygetter = lambda obj_, key_: obj_[key_]
    else:
        keys = dir(obj)
        keygetter = getattr

    conf = Config()
    for key in keys:
        if key.isupper():
            val = keygetter(obj, key)
            setattr(conf, key, val)
    return conf


def conf_from_pyfile(filename, silent=False):
    """Return the values in the config from a Python file.  This function
    behaves as if the file was imported as module with the
    :meth:`conf_from_object` function.

    :param filename: the filename of the config.  This can either be an
                     absolute filename or a filename relative to the
                     root path.
    :param silent: set to `True` if you want silent failure for missing
                   files.

    """
    globals_ = {"__file__": filename}
    locals_ = {}
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'),
                 globals_, locals_)
    except IOError as e:
        if silent and e.errno in (errno.ENOENT, errno.EISDIR):
            return False
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return conf_from_object(locals_)
