# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-05 10:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pik.core.models.uided


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20180216_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created'], 'permissions': (('change_user_comment', 'Может менять автора коментария'),), 'verbose_name': 'коментарий', 'verbose_name_plural': 'коментарии'},
        ),
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['-id'], 'permissions': (('can_edit_contact', 'Может редактировать контакты'),), 'verbose_name': 'контакт', 'verbose_name_plural': 'контакты'},
        ),
        migrations.AlterField(
            model_name='comment',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='contacts.Contact'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='uid',
            field=models.UUIDField(default=pik.core.models.uided._new_uid, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='version',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='contact',
            name='uid',
            field=models.UUIDField(default=pik.core.models.uided._new_uid, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='version',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcomment',
            name='history_type',
            field=models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalcomment',
            name='uid',
            field=models.UUIDField(db_index=True, default=pik.core.models.uided._new_uid, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcomment',
            name='version',
            field=models.IntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcontact',
            name='history_type',
            field=models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1),
        ),
        migrations.AlterField(
            model_name='historicalcontact',
            name='uid',
            field=models.UUIDField(db_index=True, default=pik.core.models.uided._new_uid, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcontact',
            name='version',
            field=models.IntegerField(editable=False),
        ),
    ]
