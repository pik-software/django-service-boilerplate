from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from .permitted import PermittedFieldsPermissionMixIn


class PermittedFieldsSerializerMixIn(PermittedFieldsPermissionMixIn):
    default_error_messages = {
        'field_permission_denied': _('У вас нет прав для '
                                     'редактирования этого поля.')
    }

    def to_internal_value(self, request_data):
        errors = {}
        ret = super().to_internal_value(request_data)
        user = self.context['request'].user
        model = self.Meta.model

        for field in ret.keys():
            if self.has_field_permission(user, model, field):
                continue
            errors[field] = [self.error_messages['field_permission_denied']]

        if errors:
            raise ValidationError(errors)

        return ret
