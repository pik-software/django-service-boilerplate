def skip_items_keys(items, keys=tuple()):
    """
    >>> skip_items_keys({'fo': 1}.items())
    [('fo', 1)]
    """
    return [x for x in items if x[0] not in keys]


def to_python_kwargs(val):
    """
    >>> to_python_kwargs({'foo': 1})
    'foo=1'
    >>> to_python_kwargs({'foo': 1, 'b': 'xx'})
    'foo=1, b=xx'
    >>> to_python_kwargs({})
    ''
    """
    return ', '.join([f"{k}={v}" for k, v in val.items()])


def to_model_field_name(name):
    return name.lstrip('_').replace('-', '_')
