# Generated by Django 2.1.2 on 2019-03-25 14:47

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_userstatistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatistics',
            name='activity',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='userstatistics',
            name='tag_stats',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
