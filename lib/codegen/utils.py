def skip_items_keys(items, keys=tuple()):
    """
    >>> skip_items_keys({'fo': 1}.items())
    [('fo', 1)]
    """
    return [x for x in items if x[0] not in keys]


def to_model_field_name(name):
    return name.lstrip('_').replace('-', '_')
