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
    "foo=1, b='xx'"
    >>> to_python_kwargs({})
    ''
    """
    return ', '.join([f"{k}={v!r}" for k, v in val.items()])


def to_model_field_name(name):
    return name.lstrip('_').replace('-', '_')


def to_model_field(schema, name=None):
    """
    >>> to_model_field({'title': ' version', 'type': 'integer', 'readOnly': True})
    "models.IntegerField(verbose_name=' version', editable=False)"
    >>> to_model_field({'title': ' uid', 'type': 'string', 'readOnly': True, 'format': 'uuid'}, name='_uid')
    "models.UUIDField(verbose_name=' uid', editable=False, primary_key=True)"
    >>> to_model_field({'title': ' uid', 'type': 'string', 'readOnly': True}, name='_uid')
    "models.CharField(verbose_name=' uid', editable=False, primary_key=True, max_length=255)"
    >>> to_model_field({'title': ' uid', 'type': 'string', 'readOnly': True, 'format': 'uuid'})
    "models.UUIDField(verbose_name=' uid', editable=False)"
    >>> to_model_field({'title': ' uid', 'type': 'string', 'readOnly': True})
    "models.CharField(verbose_name=' uid', editable=False, max_length=255)"
    >>> to_model_field({'title': 'Наименование', 'type': 'string', 'maxLength': 255, 'minLength': 1})
    "models.CharField(verbose_name='Наименование', editable=False, max_length=255)"
    >>> to_model_field({'description': 'Номера телефонов вводятся в произвольном формате через запятую', 'type': 'array', 'items': {'title': 'Phones', 'type': 'string', 'maxLength': 30, 'minLength': 1}})
    "JSONField(verbose_name='Phones', editable=False, null=True)"
    >>> to_model_field({'title': 'Индекс для сортировки', 'type': 'integer', 'maximum': 2147483647, 'minimum': -2147483648})
    "models.IntegerField(verbose_name='Индекс для сортировки', editable=False)"
    >>> to_model_field({'$ref': '#/definitions/Contact'})
    "models.ForeignKey('Contact', on_delete=models.CASCADE)"
    """
    if schema.get('$ref'):
        model = schema['$ref'][len('#/definitions/'):]
        return f"models.ForeignKey('{model}', on_delete=models.CASCADE)"
    kwargs = {'verbose_name': schema.get('title', name)}
    if schema.get('type') == 'integer':
        kwargs['editable'] = False
        return f"models.IntegerField({to_python_kwargs(kwargs)})"
    elif schema.get('type') == 'string':
        kwargs['editable'] = False
        if name == '_uid':
            kwargs['primary_key'] = True
        if schema.get('format') == 'uuid':
            return f"models.UUIDField({to_python_kwargs(kwargs)})"
        kwargs['max_length'] = schema.get('maxLength', 255)
        return f"models.CharField({to_python_kwargs(kwargs)})"
    # fix title for complex objects
    items = schema.get('items')
    if items and isinstance(items, dict) and items.get('title'):
        kwargs['verbose_name'] = items.get('title')
    kwargs['editable'] = False
    kwargs['null'] = True
    return f"JSONField({to_python_kwargs(kwargs)})"
