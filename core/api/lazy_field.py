from functools import reduce
from operator import or_

from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from rest_framework.serializers import Serializer


class LazySerializer(Serializer):
    source = None

    def __init__(self, path, ref_name=None, *args, **kwargs):  # noqa: super-init-not-called
        self.path = path
        self.args = args
        self.kwargs = kwargs
        super().__init__(path, *args, **kwargs)
        self._process_ref_name(ref_name)

    @cached_property
    def field_class(self):
        return import_string(self.path)

    @property
    def field(self):
        return self.field_class(*self.args, **self.kwargs)

    def to_internal_value(self, data):
        pass

    def to_representation(self, instance):
        pass

    def _process_ref_name(self, ref_name):
        """Resolve ref_name from source Class path"""

        if not ref_name:
            ref_name = self.path.split('.')[-1]
            if ref_name.endswith('Serializer'):
                ref_name = ref_name[:-len('Serializer')]
        self.Meta = type('Meta', (), {'ref_name': ref_name})  # noqa: invalid-name


class LazySerializerHandlerMixIn:
    def get_fields(self, *args, **kwargs):
        parents = []
        parent = self.parent
        while parent:
            parents.append(type(parent))
            parent = parent.parent

        fields = super().get_fields(*args, **kwargs)

        for name, field in list(fields.items()):
            if not isinstance(field, LazySerializer):
                continue
            is_subclass = (
                    parents and (
                    issubclass(field.field_class, tuple(parents))
                    or reduce(or_, [isinstance(parent, field.field_class)
                                    for parent in parents])))
            if is_subclass:
                if name in fields:
                    del fields[name]
                continue
            serializer = field.field
            fields[name] = serializer
        return fields
