import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindbloom.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE api_user ADD COLUMN is_admin TINYINT(1) DEFAULT 0')
    print('✓ Added is_admin column successfully')
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {str(e)}')
