import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindbloom.settings')
import django
django.setup()

from django.contrib.auth.hashers import make_password
from api.models import User

EMAIL = 'admin@example.com'
PW = 'password123'

user, created = User.objects.get_or_create(email=EMAIL, defaults={'username': 'admin', 'is_admin': True, 'password_hash': make_password(PW)})
if created:
    print('Created admin user:', EMAIL)
else:
    # ensure password and is_admin
    user.password_hash = make_password(PW)
    user.is_admin = True
    user.save()
    print('Updated admin user:', EMAIL)
