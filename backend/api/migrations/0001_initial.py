from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from datetime import date


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=80, unique=True)),
                ('email', models.CharField(max_length=120, unique=True)),
                ('password_hash', models.CharField(max_length=256)),
                ('display_name', models.CharField(blank=True, default='', max_length=100)),
                ('avatar_url', models.CharField(blank=True, default='', max_length=500)),
                ('is_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='TestDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('duration_min', models.IntegerField(default=5)),
                ('question_count', models.IntegerField(default=10)),
                ('category', models.CharField(default='personality', max_length=50)),
                ('image_color', models.CharField(default='#6C63FF', max_length=20)),
                ('is_featured', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('category', models.CharField(default='general', max_length=50)),
                ('order_num', models.IntegerField(default=0)),
            ],
            options={'ordering': ['order_num']},
        ),
        migrations.CreateModel(
            name='JournalPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journal_type', models.CharField(max_length=50)),
                ('question_text', models.TextField()),
                ('order_num', models.IntegerField(default=0)),
            ],
            options={'ordering': ['order_num']},
        ),
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('order_num', models.IntegerField(default=0)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='api.testdefinition')),
            ],
            options={'ordering': ['order_num']},
        ),
        migrations.CreateModel(
            name='DailyTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('task_type', models.CharField(default='custom', max_length=50)),
                ('completed', models.BooleanField(default=False)),
                ('task_date', models.DateField(default=date.today)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_tasks', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journal_type', models.CharField(max_length=50)),
                ('note', models.TextField(blank=True, default='')),
                ('mood', models.IntegerField(default=3)),
                ('feelings', models.TextField(blank=True, default='[]')),
                ('activities', models.TextField(blank=True, default='[]')),
                ('photo_url', models.CharField(blank=True, default='', max_length=500)),
                ('answers', models.TextField(blank=True, default='{}')),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='journal_entries', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers_json', models.TextField(blank=True, default='{}')),
                ('score', models.IntegerField(default=0)),
                ('result_summary', models.TextField(blank=True, default='')),
                ('category', models.CharField(blank=True, default='', max_length=50)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_results', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers_json', models.TextField(blank=True, default='{}')),
                ('score', models.IntegerField(default=0)),
                ('result_text', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='api.testdefinition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0.0)),
                ('severity', models.IntegerField(default=1)),
                ('reason', models.TextField(blank=True, default='')),
                ('metadata', models.TextField(blank=True, default='{}')),
                ('status', models.CharField(choices=[('new', 'New'), ('acknowledged', 'Acknowledged'), ('in_review', 'In Review'), ('resolved', 'Resolved'), ('false_positive', 'False Positive')], default='new', max_length=32)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_alerts', to='api.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='AlertAudit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=64)),
                ('note', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.user')),
                ('alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audits', to='api.alert')),
            ],
        ),
    ]
