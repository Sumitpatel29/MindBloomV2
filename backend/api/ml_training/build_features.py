import os

from api.ml_data_pipeline.feature_engineering import build_user_day_features


def build_features(data_dir, out_path):
    return build_user_day_features(data_dir, out_path)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Build engineered features from extracted parquet files')
    parser.add_argument('--data-dir', required=True, help='Directory created by extract_ml_data')
    parser.add_argument('--out', default='backend/ml_data/features.parquet', help='Output feature parquet')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    result = build_features(args.data_dir, args.out)
    print(result)


if __name__ == '__main__':
    main()
