from django.db import migrations, models


def sync_existing_status(apps, schema_editor):
    DailyTask = apps.get_model('api', 'DailyTask')
    DailyTask.objects.filter(completed=True).update(status='done')
    DailyTask.objects.filter(completed=False).update(status='pending')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_modeltrainingjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailytask',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='dailytask',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('done', 'Done'), ('missed', 'Missed')],
                default='pending',
                max_length=16,
            ),
        ),
        migrations.RunPython(sync_existing_status, migrations.RunPython.noop),
    ]
