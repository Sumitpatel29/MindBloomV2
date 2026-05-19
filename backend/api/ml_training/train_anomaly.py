import json
import os

import pandas as pd

from api.ml_models.anomaly_ensemble import load_artifacts, save_artifacts, train_ensemble


def train_from_features(feature_path, model_dir, contamination=0.1, epochs=40, batch_size=32, verbose=0):
    df = pd.read_parquet(feature_path)
    artifacts, scores = train_ensemble(
        df,
        contamination=contamination,
        epochs=epochs,
        batch_size=batch_size,
        verbose=verbose,
    )
    save_artifacts(artifacts, model_dir)
    summary = {
        'rows': int(len(df)),
        'threshold': float(artifacts.threshold),
        'score_min': float(scores.min()) if len(scores) else None,
        'score_max': float(scores.max()) if len(scores) else None,
        'score_mean': float(scores.mean()) if len(scores) else None,
        'model_dir': model_dir,
    }
    with open(os.path.join(model_dir, 'training_summary.json'), 'w', encoding='utf-8') as handle:
        json.dump(summary, handle, indent=2)
    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Train anomaly detection ensemble')
    parser.add_argument('--features', required=True, help='Path to engineered feature parquet')
    parser.add_argument('--model-dir', default='backend/ml_models', help='Directory to save model artifacts')
    parser.add_argument('--contamination', type=float, default=0.1)
    parser.add_argument('--epochs', type=int, default=40)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--verbose', type=int, default=0)
    args = parser.parse_args()

    summary = train_from_features(
        args.features,
        args.model_dir,
        contamination=args.contamination,
        epochs=args.epochs,
        batch_size=args.batch_size,
        verbose=args.verbose,
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
