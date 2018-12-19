# Generated by Django 2.1.2 on 2018-12-19 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0025_auto_20181211_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='visibility',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('PRIVATE', 'Private')], default='PRIVATE', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_groups', to='data.UserProfile'),
        ),
    ]
