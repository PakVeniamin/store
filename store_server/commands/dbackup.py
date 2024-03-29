from django.core.management import BaseCommand, call_command
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for database dump')
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--exclude=contenttypes',
            '--exclude=admin.logentry',
            '--indent=4',
            f'--output=database-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json'
        )
        self.stdout.write(self.style.SUCCESS('Database successfully backed up'))
