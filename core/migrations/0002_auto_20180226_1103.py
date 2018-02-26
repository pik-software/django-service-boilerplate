from django.db import migrations
from django.utils.translation import ugettext as _


def _create_can_post_api_import_permission(apps, schema_editor):
    user = apps.get_model("auth", "User")
    permission = apps.get_model("auth", "Permission")
    content_type = apps.get_model("contenttypes", "ContentType")
    user_content_type = content_type.objects.get_for_model(user)
    permission = permission.objects.create(
        codename='can_post_api_import',
        name=_('Может загружать данные по API.'),
        content_type=user_content_type,
    )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(_create_can_post_api_import_permission),
    ]
