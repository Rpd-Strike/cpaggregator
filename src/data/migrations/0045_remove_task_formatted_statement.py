# Generated by Django 2.2.9 on 2019-12-24 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0044_auto_20191224_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='formatted_statement',
        ),
    ]
