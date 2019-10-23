# Generated by Django 2.2.6 on 2019-10-23 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0033_auto_20191014_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='JudgeTaskStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_submitted_on', models.DateTimeField(blank=True, null=True)),
                ('total_submission_count', models.IntegerField(blank=True, null=True)),
                ('accepted_submission_count', models.IntegerField(blank=True, null=True)),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='data.Task')),
            ],
        ),
    ]
