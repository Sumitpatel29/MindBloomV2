@echo off
cd /d "E:\MindBloomV1-main reppair\MindBloomV1-main\backend"
set PYTHONPATH=%CD%
"E:\MindBloomV1-main reppair\MindBloomV1-main\backend\venv\Scripts\python.exe" manage.py run_anomaly_scoring --data-dir backend/ml_data --model-dir "E:\MindBloomV1-main reppair\MindBloomV1-main\backend\backend\ml_models" --features backend/ml_data/features.parquet --threshold 0.0
