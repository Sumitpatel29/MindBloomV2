import json
import os

import numpy as np
import pandas as pd

from api.ml_models.anomaly_ensemble import load_artifacts, score_features


def evaluate(feature_path, model_dir, out_path=None):
    df = pd.read_parquet(feature_path)
    artifacts = load_artifacts(model_dir)
    scores = score_features(artifacts, df)
    if not scores:
        report = {'rows': 0, 'alerts': 0, 'alert_rate': 0.0}
    else:
        anomaly_flags = np.array([1 if row['is_anomaly'] else 0 for row in scores])
        report = {
            'rows': int(len(scores)),
            'alerts': int(anomaly_flags.sum()),
            'alert_rate': float(anomaly_flags.mean()),
            'avg_score': float(np.mean([row['score'] for row in scores])),
            'max_score': float(np.max([row['score'] for row in scores])),
        }
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2)
    return report, scores


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate anomaly detection ensemble')
    parser.add_argument('--features', required=True, help='Path to engineered feature parquet')
    parser.add_argument('--model-dir', default='backend/ml_models', help='Directory containing model artifacts')
    parser.add_argument('--out', default='backend/ml_models/evaluation.json', help='Optional report output path')
    args = parser.parse_args()

    report, _ = evaluate(args.features, args.model_dir, args.out)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
