import os
from datetime import datetime, timedelta

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None


def _ensure_pandas():
    if pd is None:
        raise RuntimeError('pandas is required. Install with `pip install pandas`')


def build_user_day_features(parquet_folder, out_path):
    """Basic feature engineering producing one row per user per day.

    Inputs: parquet files produced by data_extractor in `parquet_folder`.
    Output: writes a Parquet file with engineered features to out_path.
    """
    _ensure_pandas()
    j_path = os.path.join(parquet_folder, 'journal_entries.parquet')
    t_path = os.path.join(parquet_folder, 'test_results.parquet')
    d_path = os.path.join(parquet_folder, 'daily_tasks.parquet')

    df_j = pd.read_parquet(j_path) if os.path.exists(j_path) else pd.DataFrame()
    df_t = pd.read_parquet(t_path) if os.path.exists(t_path) else pd.DataFrame()
    df_d = pd.read_parquet(d_path) if os.path.exists(d_path) else pd.DataFrame()

    # Normalize timestamps and dates
    if not df_j.empty:
        df_j['created_at'] = pd.to_datetime(df_j['created_at'])
        df_j['date'] = df_j['created_at'].dt.date

    if not df_t.empty:
        df_t['created_at'] = pd.to_datetime(df_t['created_at'])
        df_t['date'] = df_t['created_at'].dt.date

    if not df_d.empty:
        df_d['task_date'] = pd.to_datetime(df_d['task_date']).dt.date

    # Prepare base index: unique user/date from journal entries and tasks
    user_dates = []
    if not df_j.empty:
        user_dates += list(df_j[['user_id', 'date']].itertuples(index=False, name=None))
    if not df_d.empty:
        user_dates += list(df_d[['user_id', 'task_date']].itertuples(index=False, name=None))

    if not user_dates:
        # nothing to do
        pd.DataFrame().to_parquet(out_path, index=False)
        return out_path

    idx_df = pd.DataFrame(user_dates, columns=['user_id', 'date']).drop_duplicates()

    features = []
    for _, row in idx_df.iterrows():
        uid = row['user_id']
        date = row['date']
        # recent journal entries in last 7 days
        start = date - timedelta(days=6)
        mask = (df_j['user_id'] == uid) & (df_j['date'] >= start) & (df_j['date'] <= date) if not df_j.empty else False
        recent = df_j[mask] if not df_j.empty else pd.DataFrame()
        mood_mean = recent['mood'].mean() if not recent.empty else None
        mood_last = recent.sort_values('created_at')['mood'].iloc[-1] if not recent.empty else None
        notes_concat = ' '.join(recent['note'].fillna('').astype(str).tolist()) if not recent.empty else ''

        # tasks completed ratio that day
        tasks_mask = (df_d['user_id'] == uid) & (df_d['task_date'] == date) if not df_d.empty else False
        tasks_day = df_d[tasks_mask] if not df_d.empty else pd.DataFrame()
        tasks_completed = int(tasks_day['completed'].sum()) if not tasks_day.empty else 0
        tasks_total = len(tasks_day) if not tasks_day.empty else 0
        tasks_ratio = tasks_completed / tasks_total if tasks_total > 0 else None

        # tests taken in last 30 days
        test_mask = (df_t['user_id'] == uid) & (pd.to_datetime(df_t['created_at']).dt.date >= (date - timedelta(days=30))) if not df_t.empty else False
        tests30 = df_t[test_mask] if not df_t.empty else pd.DataFrame()
        tests_count_30 = len(tests30)

        features.append({
            'user_id': uid,
            'date': pd.to_datetime(date),
            'mood_mean_7d': mood_mean,
            'mood_last': mood_last,
            'notes_concat': notes_concat,
            'tasks_completed': tasks_completed,
            'tasks_total': tasks_total,
            'tasks_ratio': tasks_ratio,
            'tests_count_30d': tests_count_30,
        })

    df_features = pd.DataFrame(features)
    df_features.to_parquet(out_path, index=False)
    return out_path
