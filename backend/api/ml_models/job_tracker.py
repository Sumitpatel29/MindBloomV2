import json
import uuid
from django.utils import timezone

from ..models import ModelTrainingJob


def start_job(model_dir, meta=None):
    job_id = uuid.uuid4().hex
    job = ModelTrainingJob.objects.create(job_id=job_id, model_dir=model_dir, meta=json.dumps(meta or {}), status=ModelTrainingJob.STATUS_STARTED)
    return job.job_id


def update_job(model_dir, job_id, status=None, note=None):
    try:
        job = ModelTrainingJob.objects.get(job_id=job_id)
    except ModelTrainingJob.DoesNotExist:
        return None
    if status:
        job.status = status
        if status == ModelTrainingJob.STATUS_RUNNING:
            job.started_at = timezone.now()
        if status in (ModelTrainingJob.STATUS_COMPLETED, ModelTrainingJob.STATUS_FAILED):
            job.completed_at = timezone.now()
    if note:
        try:
            log = json.loads(job.log) if job.log else []
        except Exception:
            log = []
        log.append({'at': timezone.now().isoformat(), 'note': note})
        job.log = json.dumps(log)
    job.save()
    return job.to_dict()


def get_job(model_dir, job_id):
    try:
        job = ModelTrainingJob.objects.get(job_id=job_id)
        return job.to_dict()
    except ModelTrainingJob.DoesNotExist:
        return None


def list_jobs(model_dir):
    qs = ModelTrainingJob.objects.filter(model_dir=model_dir).order_by('-created_at')
    return [j.to_dict() for j in qs]
