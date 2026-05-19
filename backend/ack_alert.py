import os, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mindbloom.settings')
import django
django.setup()
from api.models import Alert, AlertAudit, User

alert = Alert.objects.order_by('created_at').first()
if not alert:
    print('no alert found')
else:
    # find an admin user if exists
    admin = User.objects.filter(is_admin=True).first()
    alert.status = Alert.STATUS_ACK
    alert.reviewed_by = admin
    from django.utils import timezone
    alert.reviewed_at = timezone.now()
    alert.save()
    audit = AlertAudit.objects.create(alert=alert, action='acknowledge', actor=admin, note='Acknowledged by script')
    print('acknowledged alert', json.dumps(alert.to_dict(), ensure_ascii=False))
    print('created audit', json.dumps(audit.to_dict(), ensure_ascii=False))
