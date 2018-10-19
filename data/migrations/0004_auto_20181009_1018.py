# Generated by Django 2.0.5 on 2018-10-09 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='judge',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='data.Judge'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='judge',
            name='judge_id',
            field=models.CharField(choices=[('ac', 'AtCoder'), ('ia', 'Infoarena'), ('poj', 'POJ')], max_length=256, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together={('judge', 'submission_id')},
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('judge', 'task_id')},
        ),
        migrations.AlterUniqueTogether(
            name='userhandle',
            unique_together={('judge', 'handle')},
        ),
    ]
