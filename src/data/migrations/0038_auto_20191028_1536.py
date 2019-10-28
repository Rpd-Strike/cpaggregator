# Generated by Django 2.2.6 on 2019-10-28 15:36

from django.db import migrations

migrate_join_table_data = """
INSERT INTO data_groupmember (group_id,profile_id,role)
  SELECT usergroup_id, userprofile_id, 'member'
  FROM data_usergroup_members
"""


class Migration(migrations.Migration):
    dependencies = [
        ('data', '0037_groupmember'),
    ]

    operations = [
        migrations.RunSQL(migrate_join_table_data)
    ]