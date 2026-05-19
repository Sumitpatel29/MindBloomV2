from django.core.management import BaseCommand, call_command

from api.seed import seed_all


class Command(BaseCommand):
    help = 'Create database tables and seed default data.'

    def handle(self, *args, **options):
        call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)
        seed_all()
        self.stdout.write(self.style.SUCCESS('Database bootstrapped successfully!'))
