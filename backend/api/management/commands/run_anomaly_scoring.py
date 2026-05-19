import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from api.ml_data_pipeline.feature_engineering import build_user_day_features
from api.ml_models.alert_service import create_alerts_from_scores
from api.ml_models.anomaly_ensemble import load_artifacts, score_features


class Command(BaseCommand):
    help = 'Build features, score anomalies, and create alerts from the latest extracted ML data.'

    def add_arguments(self, parser):
        parser.add_argument('--data-dir', default='backend/ml_data', help='Folder containing extracted parquet files')
        parser.add_argument('--model-dir', default='backend/ml_models', help='Folder containing trained model artifacts')
        parser.add_argument('--features', default='backend/ml_data/features.parquet', help='Where to write/read engineered features')
        parser.add_argument('--threshold', type=float, default=0.8, help='Alert creation threshold')

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        model_dir = options['model_dir']
        features_path = options['features']
        threshold = options['threshold']

        if not os.path.exists(model_dir):
            raise CommandError(f'Model directory not found: {model_dir}')
        if not os.path.exists(os.path.join(model_dir, 'meta.joblib')):
            raise CommandError('Model artifacts are missing. Train the anomaly model first.')

        os.makedirs(os.path.dirname(features_path), exist_ok=True)
        self.stdout.write('Building features...\n')
        build_user_day_features(data_dir, features_path)
        df = pd.read_parquet(features_path)

        self.stdout.write('Scoring features...\n')
        artifacts = load_artifacts(model_dir)
        scored = score_features(artifacts, df)
        created = create_alerts_from_scores(df, scored, threshold=threshold)

        self.stdout.write(self.style.SUCCESS(f'Scored {len(scored)} rows and created {len(created)} alerts'))
