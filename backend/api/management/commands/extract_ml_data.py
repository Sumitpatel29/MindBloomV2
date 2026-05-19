from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Extract ML training data for a date range and write parquet files to backend/ml_data/'

    def add_arguments(self, parser):
        parser.add_argument('--start', required=True, help='Start date YYYY-MM-DD')
        parser.add_argument('--end', required=True, help='End date YYYY-MM-DD')
        parser.add_argument('--out', default='backend/ml_data', help='Output folder')

    def handle(self, *args, **options):
        start = options['start']
        end = options['end']
        out = options['out']

        # lazy import to avoid app registry issues
        try:
            from api.ml_data_pipeline.data_extractor import extract_raw_data
            from api import models as api_models
        except Exception as e:
            raise CommandError(f'Failed to import extractor or models: {e}')

        self.stdout.write(f'Extracting ML data from {start} to {end} → {out}\n')
        os.makedirs(out, exist_ok=True)
        results = extract_raw_data(start, end, out, api_models)
        for k, v in results.items():
            self.stdout.write(f'Wrote {k} → {v}\n')

        self.stdout.write(self.style.SUCCESS('ML data extraction complete'))
