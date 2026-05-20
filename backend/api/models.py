from datetime import date
import json

from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=80, unique=True)
    email = models.CharField(max_length=120, unique=True)
    password_hash = models.CharField(max_length=256)

    display_name = models.CharField(max_length=100, blank=True, default='')
    avatar_url = models.CharField(max_length=500, blank=True, default='')
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Email verification + OTP (console-based)
    is_email_verified = models.BooleanField(default=False)
    otp_code_hash = models.CharField(max_length=256, blank=True, default='')
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.PositiveIntegerField(default=0)
    otp_last_sent_at = models.DateTimeField(null=True, blank=True)

    # Security timestamps
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name or self.username,
            'avatar_url': self.avatar_url,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'stats': {
                'journal_entries': self.journal_entries.count(),
                'tests_taken': self.test_results.count(),
                'assessments_done': self.assessment_results.count(),
            },
        }


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    journal_type = models.CharField(max_length=50)
    note = models.TextField(blank=True, default='')
    mood = models.IntegerField(default=3)
    feelings = models.TextField(blank=True, default='[]')
    activities = models.TextField(blank=True, default='[]')
    photo_url = models.CharField(max_length=500, blank=True, default='')
    answers = models.TextField(blank=True, default='{}')
    created_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'journal_type': self.journal_type,
            'note': self.note,
            'mood': self.mood,
            'feelings': json.loads(self.feelings) if self.feelings else [],
            'activities': json.loads(self.activities) if self.activities else [],
            'photo_url': self.photo_url,
            'answers': json.loads(self.answers) if self.answers else {},
            'created_at': self.created_at.isoformat(),
        }


class TestDefinition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    duration_min = models.IntegerField(default=5)
    question_count = models.IntegerField(default=10)
    category = models.CharField(max_length=50, default='personality')
    image_color = models.CharField(max_length=20, default='#6C63FF')
    is_featured = models.BooleanField(default=False)

    def to_dict(self, include_questions=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration_min': self.duration_min,
            'question_count': self.question_count,
            'category': self.category,
            'image_color': self.image_color,
            'is_featured': self.is_featured,
        }
        if include_questions:
            data['questions'] = [question.to_dict() for question in self.questions.all()]
        return data


class TestQuestion(models.Model):
    test = models.ForeignKey(TestDefinition, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    order_num = models.IntegerField(default=0)

    class Meta:
        ordering = ['order_num']

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'order_num': self.order_num,
        }


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(TestDefinition, on_delete=models.CASCADE, related_name='results')
    answers_json = models.TextField(blank=True, default='{}')
    score = models.IntegerField(default=0)
    result_text = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'test_title': self.test.title if self.test_id else '',
            'answers': json.loads(self.answers_json) if self.answers_json else {},
            'score': self.score,
            'result_text': self.result_text,
            'created_at': self.created_at.isoformat(),
        }


class AssessmentResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_results')
    answers_json = models.TextField(blank=True, default='{}')
    score = models.IntegerField(default=0)
    result_summary = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {
            'id': self.id,
            'answers': json.loads(self.answers_json) if self.answers_json else {},
            'score': self.score,
            'result_summary': self.result_summary,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
        }


class DailyTask(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_DONE = 'done'
    STATUS_MISSED = 'missed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_DONE, 'Done'),
        (STATUS_MISSED, 'Missed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_tasks')
    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=50, default='custom')
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    note = models.TextField(blank=True, default='')
    task_date = models.DateField(default=date.today)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'task_type': self.task_type,
            'completed': self.completed,
            'status': self.status,
            'note': self.note,
            'task_date': self.task_date.isoformat(),
        }


class JournalPrompt(models.Model):
    journal_type = models.CharField(max_length=50)
    question_text = models.TextField()
    order_num = models.IntegerField(default=0)

    class Meta:
        ordering = ['order_num']

    def to_dict(self):
        return {
            'id': self.id,
            'journal_type': self.journal_type,
            'question_text': self.question_text,
            'order_num': self.order_num,
        }


class AssessmentQuestion(models.Model):
    question_text = models.TextField()
    category = models.CharField(max_length=50, default='general')
    order_num = models.IntegerField(default=0)

    class Meta:
        ordering = ['order_num']

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'category': self.category,
            'order_num': self.order_num,
        }


class Alert(models.Model):
    STATUS_NEW = 'new'
    STATUS_ACK = 'acknowledged'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_RESOLVED = 'resolved'
    STATUS_FALSE = 'false_positive'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_ACK, 'Acknowledged'),
        (STATUS_IN_REVIEW, 'In Review'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_FALSE, 'False Positive'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    score = models.FloatField(default=0.0)
    severity = models.IntegerField(default=1)  # 1-5
    reason = models.TextField(blank=True, default='')
    metadata = models.TextField(blank=True, default='{}')  # JSON string with contributing features
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_alerts')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score': self.score,
            'severity': self.severity,
            'reason': self.reason,
            'metadata': json.loads(self.metadata) if self.metadata else {},
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'reviewed_by': self.reviewed_by_id,
            'reviewed_by_user': self.reviewed_by.to_dict() if self.reviewed_by else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class AlertAudit(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='audits')
    action = models.CharField(max_length=64)  # e.g., 'acknowledge', 'resolve', 'dismiss'
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'action': self.action,
            'actor_id': self.actor_id,
            'actor': self.actor.to_dict() if self.actor else None,
            'note': self.note,
            'created_at': self.created_at.isoformat(),
        }


class ModelTrainingJob(models.Model):
    STATUS_STARTED = 'started'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_STARTED, 'Started'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    job_id = models.CharField(max_length=64, unique=True)
    model_dir = models.CharField(max_length=400, blank=True, default='')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_STARTED)
    meta = models.TextField(blank=True, default='{}')
    log = models.TextField(blank=True, default='[]')
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def to_dict(self):
        try:
            meta = json.loads(self.meta) if self.meta else {}
        except Exception:
            meta = {}
        try:
            log = json.loads(self.log) if self.log else []
        except Exception:
            log = []
        return {
            'id': self.id,
            'job_id': self.job_id,
            'model_dir': self.model_dir,
            'status': self.status,
            'meta': meta,
            'log': log,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
