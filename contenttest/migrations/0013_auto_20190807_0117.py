# Generated by Django 2.2.3 on 2019-08-07 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttest', '0012_auto_20190807_0114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='star',
            name='car',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='starset', related_query_name='starquery', to='contenttest.Car'),
        ),
    ]
