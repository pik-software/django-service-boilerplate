from django.contrib import admin

from .models import EntityType, Entity

admin.site.register(
    EntityType,
    list_display=['slug', 'name', 'schema'],
    search_fields=['slug', 'name'],
    date_hierarchy='created',
)

admin.site.register(
    Entity,
    list_display=['type', 'value', 'created', 'updated', 'version'],
    search_fields=['value'],
    list_filter=['type'],
    date_hierarchy='created',
)
