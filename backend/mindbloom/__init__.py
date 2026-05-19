import pymysql

pymysql.install_as_MySQLdb()

# Ensure shared Celery tasks use the configured Django app.
from .celery import app as celery_app

__all__ = ('celery_app',)
