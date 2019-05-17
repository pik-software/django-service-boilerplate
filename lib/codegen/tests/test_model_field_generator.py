from lib.codegen.model_field_generator import ModelFieldGenerator


class TestModelFieldGenerator:

    GENERATOR = ModelFieldGenerator()

    def generate(self, schema, name=None):
        return self.GENERATOR(schema, name=name)

    def test_create_integer_field(self):
        schema = {'title': 'version', 'type': 'integer', 'readOnly': True}
        assert self.generate(schema) == (
            "models.IntegerField(verbose_name='version', editable=False, "
            "null=True)")

    def test_create_uuid_field(self):
        schema = {
            'title': 'uid', 'type': 'string', 'readOnly': True,
            'format': 'uuid'}
        assert self.generate(schema) == (
            "models.UUIDField(verbose_name='uid', editable=False, null=True)")

    def test_create_protocol_char_field(self):
        # IF field name in API start's with underscore.
        # It will have title starting with white space.
        # Probably a bug in schema generation.
        schema = {
            'title': ' type', 'type': 'string', 'readOnly': True}
        assert self.generate(schema) == (
            "models.CharField(verbose_name='type', editable=False, "
            "null=True, max_length=255)")

    def test_create_uid_pk_field(self):
        schema = {
            'title': '_uid', 'type': 'string', 'readOnly': True,
            'format': 'uuid'}
        assert self.generate(schema, name='_uid') == (
            "models.UUIDField(verbose_name='uid', primary_key=True)")

    def test_create_char_pk_field(self):
        schema = {
            'title': 'uid', 'type': 'string', 'readOnly': True}
        assert self.generate(schema, name='_uid') == (
            "models.CharField(verbose_name='uid', primary_key=True, "
            "max_length=255)")

    def test_create_char_field(self):
        schema = {
            'title': 'Наименование', 'type': 'string', 'maxLength': 510,
            'minLength': 1}
        assert self.generate(schema) == (
            "models.CharField(verbose_name='Наименование', editable=False, "
            "null=True, max_length=255)")

    def test_create_date_field(self):
        schema = {
            'title': 'Дата рождения', 'type': 'string', 'format': 'date'}
        assert self.generate(schema) == (
            "models.DateField(verbose_name='Дата рождения', editable=False, "
            "null=True)")

    def test_create_datetime_field(self):
        schema = {'title': 'Удален', 'type': 'string', 'format': 'date-time'}
        assert self.generate(schema) == (
            "models.DateTimeField(verbose_name='Удален', editable=False, "
            "null=True)")

    def test_create_boolean_field(self):
        schema = {
            'title': 'Используется', 'type': 'boolean', 'readOnly': True}
        assert self.generate(schema) == (
            "models.BooleanField(verbose_name='Используется', editable=False, "
            "null=True)")

    def test_create_foreign_key_field(self):
        schema = {'$ref': '#/definitions/Contact'}
        assert self.generate(schema) == (
            "models.ForeignKey('Contact', editable=False, null=True, "
            "on_delete=models.CASCADE)")

    def test_create_json_field_for_array(self):
        schema = {
            'description': ('Номера телефонов в произвольном формате'),
            'type': 'array', 'items': {
                'title': 'Phones', 'type': 'string', 'maxLength': 30,
                'minLength': 1}}
        assert self.generate(schema) == (
            "JSONField(verbose_name='Phones', editable=False, default=dict)")
