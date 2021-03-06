# Generated by Django 2.1.2 on 2018-10-31 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cors', '0004_auto_20180606_0836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cors',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='cors',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='updated'),
        ),
        migrations.AlterField(
            model_name='historicalcors',
            name='created',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='historicalcors',
            name='updated',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='updated'),
        ),
    ]
