# Generated by Django 3.0.5 on 2020-08-16 20:07

from django.db import migrations
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('ladders', '0003_auto_20200816_1704'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='laddertask',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('started_on'), nulls_last=True)]},
        ),
        migrations.RemoveField(
            model_name='laddertask',
            name='level',
        ),
    ]