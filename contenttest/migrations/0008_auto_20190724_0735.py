# Generated by Django 2.2.3 on 2019-07-24 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttest', '0007_auto_20190722_0740'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='personchild',
            name='person_ptr',
        ),
        migrations.DeleteModel(
            name='CountPeople',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
        migrations.DeleteModel(
            name='PersonChild',
        ),
    ]
