# Generated by Django 2.2.9 on 2019-12-24 22:51

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0047_auto_20191224_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskstatement',
            name='examples',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
