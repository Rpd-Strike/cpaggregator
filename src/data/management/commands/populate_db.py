import argparse
import os

from django.core.management.base import BaseCommand
import csv

from cpaggregator.settings import BASE_DIR
from data.models import Task
from data.populate import create_judge, create_user, create_user_handle, create_task
from scraper.database import get_db
from scraper.services import scrape_submissions_for_task

ASD_USERS_CSV_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "management", "files", "asd_users.csv")
ASD_TASKS_CSV_PATH = os.path.join(os.path.dirname(BASE_DIR), "data", "management", "files", "asd_tasks.csv")


def _create_judges():
    create_judge(
        judge_id='ac',
        name='AtCoder',
        homepage='https://www.atcoder.jp/',
    )
    create_judge(
        judge_id='ia',
        name='Infoarena',
        homepage='https://www.infoarena.ro/',
    )
    create_judge(
        judge_id='poj',
        name='POJ',
        homepage='http://poj.org/',
    )
    create_judge(
        judge_id='csa',
        name='CSAcademy',
        homepage='http://www.csacademy.com/',
    )


def _create_tasks():
    # Seminar ASD.
    with open(ASD_TASKS_CSV_PATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_task(task_id=row['Task Id'])


def _create_users():
    # Seminar ASD.
    with open(ASD_USERS_CSV_PATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            names = row['Nume & Prenume'].split()
            first_names = names[1:]
            last_name = names[0]
            username = "".join(first_names) + last_name
            # Create user in database.
            create_user(
                username=username,
                first_name="-".join(first_names),
                last_name=last_name
            )

            # Link infoarena username.
            if row.get('Handle infoarena', "") != "":
                create_user_handle(
                    username=username,
                    judge_id='ia',
                    handle=row['Handle infoarena'],
                )

            # Link csacademy username.
            if row.get('Handle CSAcademy', "") != "":
                create_user_handle(
                    username=username,
                    judge_id='csa',
                    handle=row['Handle CSAcademy'],
                )


def _create_submissions(queryset):
    db = get_db()
    for task in queryset:
        task_id = ":".join([task.judge.judge_id, task.task_id])
        print("Scraping submissions for: %s" % task_id)
        scrape_submissions_for_task(db, task_id)


class Command(BaseCommand):
    help = 'Populates the database.'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('days', type=int, default=1)
        parser.add_argument('tasks', nargs='*')

    def handle(self, *args, **options):
        _create_judges()
        _create_tasks()
        _create_users()
        _create_submissions()
