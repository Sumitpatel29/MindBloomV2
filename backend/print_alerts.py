import os, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mindbloom.settings')
import django
django.setup()
from api.models import Alert
qs = Alert.objects.all().order_by('-created_at')
print('alerts count:', qs.count())
for a in qs[:10]:
    print(json.dumps(a.to_dict(), ensure_ascii=False))
