# Generated by Django 2.1.2 on 2019-03-26 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0022_tasksheet_tasks'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='use_best_recent',
            field=models.BooleanField(default=False),
        ),
    ]
