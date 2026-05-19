@echo off
REM Change working directory to the script's folder (the `backend` dir)
cd /d "%~dp0"
set PYTHONPATH=%CD%
REM Prefer a local venv if present, otherwise fall back to system `python`
if exist "%~dp0venv\Scripts\python.exe" (
	"%~dp0venv\Scripts\python.exe" manage.py run_anomaly_scoring --data-dir ml_data --model-dir ml_models --features ml_data/features.parquet --threshold 0.0
) else (
	python manage.py run_anomaly_scoring --data-dir ml_data --model-dir ml_models --features ml_data/features.parquet --threshold 0.0
)
