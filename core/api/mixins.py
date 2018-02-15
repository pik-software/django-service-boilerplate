from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response


class BulkCreateModelMixin(CreateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializers ``many=True``.
    
    Example:
        
        class ContactViewSet(StandartizedModelViewSet):
            ...
            allow_bulk_create = True
            ...
        
    """
    allow_bulk_create = False

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)

        if not bulk:
            return super().create(request, *args, **kwargs)

        if not self.allow_bulk_create:
            raise ValidationError(
                'You do not have permission to create multiple objects')

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        return self.perform_create(serializer)
