class ModelFieldGenerator:

    UUID_MODEL_FIELD_NAME = 'models.UUIDField'
    DATE_MODEL_FIELD_NAME = 'models.DateField'
    DATETIME_MODEL_FIELD_NAME = 'models.DateTimeField'
    FOREIGN_KEY_MODEL_FIELD_NAME = 'models.ForeignKey'
    INTEGER_MODEL_FIELD_NAME = 'models.IntegerField'
    JSON_MODEL_FIELD_NAME = 'JSONField'
    CHAR_MODEL_FIELD_NAME = 'models.CharField'
    BOOLEAN_MODEL_FIELD_NAME = 'models.BooleanField'

    DEFAULT_MODEL_FIELD_NAME = JSON_MODEL_FIELD_NAME
    DEFAULT_CHAR_MODEL_FIELD_MAX_LENGTH = 255

    STRING_TYPE = 'string'
    INTEGER_TYPE = 'integer'
    BOOLEAN_TYPE = 'boolean'

    STRING_FORMAT_TO_FIELD_NAME = {
        'uuid': UUID_MODEL_FIELD_NAME,
        'date': DATE_MODEL_FIELD_NAME,
        'date-time': DATETIME_MODEL_FIELD_NAME, }

    DEFAULT_FIELD_KWARGS = {
        'editable': False,
        'null': True}

    @staticmethod
    def _to_python_kwargs(val):
        """
        >>> ModelFieldGenerator._to_python_kwargs({'foo': 1})
        'foo=1'
        >>> ModelFieldGenerator._to_python_kwargs({'foo': 1, 'b': 'xx'})
        'foo=1, b=xx'
        >>> ModelFieldGenerator._to_python_kwargs({})
        ''
        """
        return ', '.join([f"{k}={v}" for k, v in val.items()])

    def _get_field_name_from_format(self, field_format):
        return self.STRING_FORMAT_TO_FIELD_NAME.get(
            field_format, self.CHAR_MODEL_FIELD_NAME)

    @staticmethod
    def get_field_refs(schema):
        if '$ref' in schema:
            return [schema['$ref']]

        return [
            item['$ref']
            for keyword in ['anyOf', 'allOf', 'oneOf'] if keyword in schema
            for item in schema[keyword] if '$ref' in item]

    def get_model_field_name(self, schema):
        property_type = schema.get('type')

        # TODO: asklimenko Add generic FK support
        refs = self.get_field_refs(schema)
        if refs:
            model_field_name = self.FOREIGN_KEY_MODEL_FIELD_NAME
        elif property_type == self.STRING_TYPE:
            field_format = schema.get('format', 'unknown')
            model_field_name = self._get_field_name_from_format(field_format)
        elif property_type == self.INTEGER_TYPE:
            model_field_name = self.INTEGER_MODEL_FIELD_NAME
        elif property_type == self.BOOLEAN_TYPE:
            model_field_name = self.BOOLEAN_MODEL_FIELD_NAME
        else:
            model_field_name = self.DEFAULT_MODEL_FIELD_NAME
        return model_field_name

    def _get_field_args(self, schema, field_name):
        # TODO: asklimenko Add generic foreign key support
        if field_name == self.FOREIGN_KEY_MODEL_FIELD_NAME:
            refs = self.get_field_refs(schema)
            model_ref = refs[0].split('/')[-1]
            return [f"'{model_ref}'"]
        return []

    def _get_field_kwargs(self, schema, model_field_name, name=None):
        verbose_name = schema.get('title')

        if verbose_name:
            # IF field name in API start's with underscore.
            # It will have title starting with white space.
            # Probably a bug in schema generation.
            verbose_name = verbose_name.lstrip()
            verbose_name = verbose_name.lstrip('_')
        kwargs = {'verbose_name': repr(verbose_name)}
        kwargs.update(self.DEFAULT_FIELD_KWARGS)

        if name == '_uid':
            kwargs['primary_key'] = True
            kwargs.pop('null', None)
            kwargs.pop('editable', None)

            if model_field_name == self.CHAR_MODEL_FIELD_NAME:
                kwargs['max_length'] = self.DEFAULT_CHAR_MODEL_FIELD_MAX_LENGTH

        elif model_field_name == self.CHAR_MODEL_FIELD_NAME:
            kwargs['max_length'] = self.DEFAULT_CHAR_MODEL_FIELD_MAX_LENGTH

        elif model_field_name == self.FOREIGN_KEY_MODEL_FIELD_NAME:
            kwargs.pop('verbose_name', None)
            kwargs['on_delete'] = 'models.CASCADE'

        elif model_field_name == self.JSON_MODEL_FIELD_NAME:
            items = schema.get('items')
            if items and isinstance(items, dict) and items.get('title'):
                kwargs['verbose_name'] = repr(items.get('title'))

            kwargs.pop('null', None)
            kwargs['default'] = 'dict'

        return kwargs

    def _construct_field_definition(
            self, model_field_name, field_args, field_kwargs):

        if field_args:
            args = ", ".join(field_args) + ', '
        else:
            args = ''

        kwargs = self._to_python_kwargs(field_kwargs)
        return f"{model_field_name}({args}{kwargs})"

    def __call__(self, schema, name=None):
        model_field_name = self.get_model_field_name(schema)
        args = self._get_field_args(schema, model_field_name)
        kwargs = self._get_field_kwargs(schema, model_field_name, name)
        return self._construct_field_definition(model_field_name, args, kwargs)
