# Generated by Django 2.2.3 on 2019-07-22 06:44

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('contenttest', '0004_remove_taggeditem_object_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('role', models.CharField(choices=[('A', 'Author'), ('E', 'Editor')], max_length=1)),
            ],
            managers=[
                ('people', django.db.models.manager.Manager()),
            ],
        ),
        migrations.DeleteModel(
            name='Bookmark',
        ),
        migrations.DeleteModel(
            name='TaggedItem',
        ),
    ]
