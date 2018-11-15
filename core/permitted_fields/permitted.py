class PermittedFieldsPermissionMixIn:
    def has_field_permission(self, user, model, field):
        permitted_fields = getattr(self, 'permitted_fields',
                                   getattr(model, 'permitted_fields', None))
        if not permitted_fields:
            return False
        for permission, _fields in permitted_fields.items():
            meta = model._meta  # noqa: protected-access
            permission = permission.format(app_label=meta.app_label.lower(),
                                           model_name=meta.object_name.lower())
            has_perm = (field in _fields and user.has_perm(permission))
            if has_perm:
                return True
        return False
