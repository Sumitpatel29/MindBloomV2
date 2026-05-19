from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(100), default='')
    avatar_url = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True)
    test_results = db.relationship('TestResult', backref='user', lazy=True)
    assessment_results = db.relationship('AssessmentResult', backref='user', lazy=True)
    daily_tasks = db.relationship('DailyTask', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name or self.username,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'stats': {
                'journal_entries': len(self.journal_entries),
                'tests_taken': len(self.test_results),
                'assessments_done': len(self.assessment_results),
            }
        }


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    journal_type = db.Column(db.String(50), nullable=False)  # release_worry, calm_anxiety, feeling_angry, feeling_happy
    note = db.Column(db.Text, default='')
    mood = db.Column(db.Integer, default=3)  # 1-5 scale
    feelings = db.Column(db.Text, default='[]')  # JSON array
    activities = db.Column(db.Text, default='[]')  # JSON array
    photo_url = db.Column(db.String(500), default='')
    answers = db.Column(db.Text, default='{}')  # JSON - answers to guided questions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
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


class TestDefinition(db.Model):
    __tablename__ = 'test_definitions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    duration_min = db.Column(db.Integer, default=5)
    question_count = db.Column(db.Integer, default=10)
    category = db.Column(db.String(50), default='personality')
    image_color = db.Column(db.String(20), default='#6C63FF')
    is_featured = db.Column(db.Boolean, default=False)

    questions = db.relationship('TestQuestion', backref='test', lazy=True, order_by='TestQuestion.order_num')

    def to_dict(self, include_questions=False):
        d = {
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
            d['questions'] = [q.to_dict() for q in self.questions]
        return d


class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test_definitions.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    order_num = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'order_num': self.order_num,
        }


class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test_definitions.id'), nullable=False)
    answers_json = db.Column(db.Text, default='{}')
    score = db.Column(db.Integer, default=0)
    result_text = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    test = db.relationship('TestDefinition', backref='results')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'test_id': self.test_id,
            'test_title': self.test.title if self.test else '',
            'answers': json.loads(self.answers_json) if self.answers_json else {},
            'score': self.score,
            'result_text': self.result_text,
            'created_at': self.created_at.isoformat(),
        }


class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers_json = db.Column(db.Text, default='{}')
    score = db.Column(db.Integer, default=0)
    result_summary = db.Column(db.Text, default='')
    category = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'answers': json.loads(self.answers_json) if self.answers_json else {},
            'score': self.score,
            'result_summary': self.result_summary,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
        }


class DailyTask(db.Model):
    __tablename__ = 'daily_tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), default='custom')  # good_deed, relaxing_game, custom
    completed = db.Column(db.Boolean, default=False)
    task_date = db.Column(db.Date, default=date.today)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'task_type': self.task_type,
            'completed': self.completed,
            'task_date': self.task_date.isoformat(),
        }


class JournalPrompt(db.Model):
    __tablename__ = 'journal_prompts'
    id = db.Column(db.Integer, primary_key=True)
    journal_type = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    order_num = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'journal_type': self.journal_type,
            'question_text': self.question_text,
            'order_num': self.order_num,
        }


class AssessmentQuestion(db.Model):
    __tablename__ = 'assessment_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    order_num = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'category': self.category,
            'order_num': self.order_num,
        }
