import os
import json
from datetime import datetime

from celery import shared_task


@shared_task(bind=True)
def retrain_model_task(self, job_id, model_dir, feature_path, contamination=0.1, epochs=40, batch_size=32):
    """Celery task wrapper for retraining models using existing training script.
    This updates the DB-backed job tracker while running.
    """
    try:
        from .ml_models import job_tracker
        job_tracker.update_job(model_dir, job_id, status='running', note='Celery task started')
        # Run the training function directly to keep logs in-process
        from .ml_training.train_anomaly import train_from_features
        summary = train_from_features(feature_path, model_dir, contamination=contamination, epochs=epochs, batch_size=batch_size, verbose=1)
        job_tracker.update_job(model_dir, job_id, status='completed', note=f"Training completed: rows={summary.get('rows')}")
    except Exception as exc:
        try:
            job_tracker.update_job(model_dir, job_id, status='failed', note=f'Error: {exc}')
        except Exception:
            pass
        raise
