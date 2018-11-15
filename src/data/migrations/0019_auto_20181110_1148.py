# Generated by Django 2.1.2 on 2018-11-10 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_auto_20181106_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='MethodTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_id', models.CharField(max_length=256, unique=True)),
                ('tag_name', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='memory_limit_kb',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='time_limit_ms',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='tags',
            field=models.ManyToManyField(to='data.MethodTag'),
        ),
    ]