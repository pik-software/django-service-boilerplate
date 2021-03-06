# Generated by Django 2.1.3 on 2019-01-29 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cors', '0005_auto_20181031_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cors',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='cors',
            name='updated',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='updated'),
        ),
        migrations.AlterField(
            model_name='historicalcors',
            name='created',
            field=models.DateTimeField(blank=True, db_index=True, editable=False, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='historicalcors',
            name='updated',
            field=models.DateTimeField(blank=True, db_index=True, editable=False, verbose_name='updated'),
        ),
    ]
