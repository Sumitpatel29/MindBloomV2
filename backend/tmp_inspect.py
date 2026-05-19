import pandas as pd, os
folder='backend/ml_data'
files=['journal_entries.parquet','daily_tasks.parquet','test_results.parquet','users.parquet']
for fname in files:
    p=os.path.join(folder,fname)
    print(fname, 'exists', os.path.exists(p))
    if os.path.exists(p):
        df=pd.read_parquet(p)
        print(' rows', len(df))
        print(' cols', list(df.columns))
