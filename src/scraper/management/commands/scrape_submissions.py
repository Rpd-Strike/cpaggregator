import argparse

from django.core.management.base import BaseCommand
import datetime

from scraper import services, database


class Command(BaseCommand):
    help = 'Populates the database.'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--from_days', type=int, default=0)
        parser.add_argument('--to_days', type=int, default=1)
        parser.add_argument('--tasks', nargs='+')

    def handle(self, *args, **options):
        services.scrape_submissions_for_tasks(
            *options['tasks'],
            from_days=options['from_days'],
            to_days=options['to_days'],
        )