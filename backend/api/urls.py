from django.urls import path

from . import views

urlpatterns = [
    path('auth/register', views.register),
    path('auth/verify-otp', views.verify_otp),
    path('auth/login', views.login),

    path('auth/me', views.me),
    path('home/tasks', views.tasks),
    path('home/tasks/<int:task_id>', views.toggle_task),
    path('home/analyze-day', views.analyze_day),
    path('home/quest', views.quest),
    path('home/suggestions', views.suggestions),
    path('journal/options', views.journal_options),
    path('journal/prompts/<str:journal_type>', views.journal_prompts),
    path('journal/entries', views.journal_entries),
    path('tests', views.tests_list),
    path('tests/<int:test_id>', views.test_detail),
    path('tests/<int:test_id>/submit', views.submit_test),
    path('tests/results', views.test_results),
    path('growth/assessment', views.assessment),
    path('growth/results', views.assessment_results),
    path('profile', views.profile),
    path('profile/change-password', views.change_password),
    path('admin/alerts', views.admin_alerts),
    path('admin/alerts/stats', views.admin_alert_stats),
    path('admin/alerts/score', views.admin_alert_score),
    path('admin/models/retrain', views.admin_model_retrain),
    path('admin/models/jobs', views.admin_model_jobs_list),
    path('admin/models/jobs/<str:job_id>', views.admin_model_job_status),
    path('admin/alerts/<int:alert_id>', views.admin_alert_detail),
    path('admin/alerts/<int:alert_id>/acknowledge', views.admin_alert_acknowledge),
    path('admin/alerts/<int:alert_id>/resolve', views.admin_alert_resolve),
]
