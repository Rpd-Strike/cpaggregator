# Generated by Django 2.1.2 on 2019-03-26 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0020_auto_20190326_1113'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasksheettask',
            options={'ordering': ['ordering_id']},
        ),
        migrations.RemoveField(
            model_name='tasksheet',
            name='tasks',
        ),
        migrations.AddField(
            model_name='tasksheettask',
            name='ordering_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
