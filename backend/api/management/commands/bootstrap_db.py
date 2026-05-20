import time
import os

from django.core.management import BaseCommand, call_command
from django.db import OperationalError

from api.seed import seed_all


class Command(BaseCommand):
    help = 'Create database tables and seed default data.'

    def handle(self, *args, **options):
        database_url = (
            os.environ.get('DATABASE_URL', '')
            or os.environ.get('MYSQL_URL', '')
            or os.environ.get('CLEARDB_DATABASE_URL', '')
            or os.environ.get('JAWSDB_URL', '')
        )
        mysql_host = (os.environ.get('MYSQL_HOST', '') or os.environ.get('MYSQLHOST', '')).strip()
        mysql_name = (os.environ.get('MYSQL_DATABASE', '') or os.environ.get('MYSQLDATABASE', '')).strip()

        if not (database_url or (mysql_host and mysql_name)):
            self.stdout.write(self.style.WARNING('No MySQL configuration found; skipping bootstrap and using the configured database backend.'))
            return

        last_exc = None
        for attempt in range(1, 11):
            try:
                call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
                last_exc = None
                break
            except OperationalError as e:
                last_exc = e
                time.sleep(3)

        # Only seed when migrations succeeded.
        if last_exc is None:
            seed_all()
            self.stdout.write(self.style.SUCCESS('Database bootstrapped successfully!'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Database bootstrap skipped because migrations failed after retries: {last_exc}'
                )
            )
            self.stdout.write(self.style.WARNING('App will start; DB-backed endpoints may fail until DB is reachable.'))

