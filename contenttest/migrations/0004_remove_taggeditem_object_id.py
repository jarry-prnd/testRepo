# Generated by Django 2.2.3 on 2019-07-22 04:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttest', '0003_remove_taggeditem_test_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taggeditem',
            name='object_id',
        ),
    ]
