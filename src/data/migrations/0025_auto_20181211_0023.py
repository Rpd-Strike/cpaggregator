# Generated by Django 2.1.2 on 2018-12-11 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_userhandle_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='group_id',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
