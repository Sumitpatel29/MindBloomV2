import os
from datetime import datetime, time

from django.utils import timezone

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


def _ensure_pandas():
    if pd is None:
        raise RuntimeError('pandas is required. Install with `pip install pandas`')


def extract_raw_data(start_date, end_date, out_dir, models):
    """Extract raw tables (journal entries, test results, daily tasks, users) into CSV/Parquet.

    Args:
        start_date (date or str): inclusive start date (YYYY-MM-DD)
        end_date (date or str): inclusive end date (YYYY-MM-DD)
        out_dir (str): output directory for files
        models: import of api.models module (to avoid circular imports)
    Returns:
        dict: paths of written files
    """
    _ensure_pandas()
    os.makedirs(out_dir, exist_ok=True)

    # Parse dates and make them timezone-aware to avoid Django warnings.
    def _parse_bound(value, is_end=False):
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value)
        else:
            parsed = value

        if isinstance(parsed, datetime):
            bound = parsed
        else:
            bound = datetime.combine(parsed, time.max if is_end else time.min)

        if timezone.is_naive(bound):
            bound = timezone.make_aware(bound, timezone.get_current_timezone())
        return bound

    start = _parse_bound(start_date, is_end=False)
    end = _parse_bound(end_date, is_end=True)

    results = {}

    # Journal entries
    journals_qs = models.JournalEntry.objects.filter(created_at__range=(start, end)).select_related('user')
    journals = []
    for j in journals_qs:
        journals.append({
            'id': j.id,
            'user_id': j.user_id,
            'username': j.user.username if j.user else '',
            'created_at': j.created_at.isoformat(),
            'mood': j.mood,
            'note': j.note,
            'feelings': j.feelings,
            'activities': j.activities,
        })
    df_j = pd.DataFrame(journals)
    j_path = os.path.join(out_dir, 'journal_entries.parquet')
    df_j.to_parquet(j_path, index=False)
    results['journal_entries'] = j_path

    # Test results
    tests_qs = models.TestResult.objects.filter(created_at__range=(start, end)).select_related('user', 'test')
    tests = []
    for t in tests_qs:
        tests.append({
            'id': t.id,
            'user_id': t.user_id,
            'test_id': t.test_id,
            'test_title': t.test.title if t.test else '',
            'score': t.score,
            'created_at': t.created_at.isoformat(),
        })
    df_t = pd.DataFrame(tests)
    t_path = os.path.join(out_dir, 'test_results.parquet')
    df_t.to_parquet(t_path, index=False)
    results['test_results'] = t_path

    # Daily tasks
    tasks_qs = models.DailyTask.objects.filter(task_date__range=(start.date(), end.date())).select_related('user')
    tasks = []
    for d in tasks_qs:
        tasks.append({
            'id': d.id,
            'user_id': d.user_id,
            'title': d.title,
            'completed': bool(d.completed),
            'task_date': d.task_date.isoformat(),
        })
    df_d = pd.DataFrame(tasks)
    d_path = os.path.join(out_dir, 'daily_tasks.parquet')
    df_d.to_parquet(d_path, index=False)
    results['daily_tasks'] = d_path

    # Users summary
    users_qs = models.User.objects.all()
    users = []
    for u in users_qs:
        users.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'display_name': u.display_name,
            'created_at': u.created_at.isoformat(),
        })
    df_u = pd.DataFrame(users)
    u_path = os.path.join(out_dir, 'users.parquet')
    df_u.to_parquet(u_path, index=False)
    results['users'] = u_path

    return results
