import time

from django.core.management import BaseCommand, call_command
from django.db import OperationalError

from api.seed import seed_all


class Command(BaseCommand):
    help = 'Create database tables and seed default data.'

    def handle(self, *args, **options):
        for attempt in range(1, 11):
            try:
                call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
                break
            except OperationalError:
                if attempt == 10:
                    raise
                time.sleep(3)
        seed_all()
        self.stdout.write(self.style.SUCCESS('Database bootstrapped successfully!'))
