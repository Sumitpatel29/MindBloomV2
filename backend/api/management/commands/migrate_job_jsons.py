from django.core.management.base import BaseCommand
import glob
import json
import os
from datetime import datetime

from api.models import ModelTrainingJob


class Command(BaseCommand):
    help = "Migrate legacy job JSON files into ModelTrainingJob records"

    def add_arguments(self, parser):
        parser.add_argument('--path', default='backend/**/ml_models/*.json', help='glob path to search for job jsons')

    def handle(self, *args, **options):
        path = options['path']
        files = glob.glob(path, recursive=True)
        created = 0
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping {f}: cannot read/parse ({e})"))
                continue

            job_id = data.get('job_id') or os.path.splitext(os.path.basename(f))[0]
            if ModelTrainingJob.objects.filter(job_id=job_id).exists():
                self.stdout.write(self.style.NOTICE(f"Job {job_id} already exists, skipping"))
                continue

            status = data.get('status', 'completed')
            meta = data
            log = json.dumps(data.get('log', {}), ensure_ascii=False) if isinstance(data.get('log', {}), dict) else str(data.get('log', ''))

            job = ModelTrainingJob.objects.create(
                job_id=job_id,
                status=status,
                meta=meta,
                log=log,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created} jobs"))
