# Generated by Django 2.2.6 on 2019-10-26 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0035_auto_20191023_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='statement',
            field=models.TextField(blank=True, null=True),
        ),
    ]