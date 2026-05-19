import json
import os
from dataclasses import dataclass

import joblib
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


NUMERIC_FEATURES = [
    'mood_mean_7d',
    'mood_last',
    'tasks_completed',
    'tasks_total',
    'tasks_ratio',
    'tests_count_30d',
    'note_length',
    'note_sentiment',
    'note_risk_keywords',
]


def _require_tensorflow():
    try:
        import tensorflow as tf  # type: ignore
        return tf
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            'tensorflow is required for the autoencoder. Install with `pip install tensorflow`.'
        ) from exc


def _safe_sentiment(text):
    if not text:
        return 0.0
    text = str(text).lower()
    positive = ['good', 'better', 'happy', 'calm', 'hope', 'strong', 'love']
    negative = ['sad', 'anxious', 'angry', 'hopeless', 'worthless', 'cry', 'hurt']
    pos = sum(word in text for word in positive)
    neg = sum(word in text for word in negative)
    total = pos + neg
    if total == 0:
        return 0.0
    return float((pos - neg) / total)


def _risk_keyword_count(text):
    if not text:
        return 0.0
    text = str(text).lower()
    keywords = [
        'hopeless', 'worthless', 'suicide', 'kill myself', 'self harm', 'end it',
        'can\'t take it', 'no reason to live', 'want to disappear'
    ]
    return float(sum(kw in text for kw in keywords))


def prepare_feature_frame(df):
    """Create the numeric feature matrix used by the anomaly detector."""
    if df is None or df.empty:
        return np.empty((0, len(NUMERIC_FEATURES))), []

    work = df.copy()
    if 'notes_concat' not in work.columns:
        work['notes_concat'] = ''
    work['note_length'] = work['notes_concat'].fillna('').astype(str).str.len().astype(float)
    work['note_sentiment'] = work['notes_concat'].fillna('').astype(str).map(_safe_sentiment).astype(float)
    work['note_risk_keywords'] = work['notes_concat'].fillna('').astype(str).map(_risk_keyword_count).astype(float)

    for column in NUMERIC_FEATURES:
        if column not in work.columns:
            work[column] = np.nan

    return work[NUMERIC_FEATURES].astype(float).to_numpy(), list(work.index)


@dataclass
class EnsembleArtifacts:
    isolation_forest: object
    scaler: object
    autoencoder: object
    threshold: float
    feature_names: list


def build_autoencoder(input_dim, encoding_dim=4):
    tf = _require_tensorflow()
    from tensorflow import keras  # type: ignore

    inputs = keras.Input(shape=(input_dim,))
    x = keras.layers.Dense(max(8, input_dim * 2), activation='relu')(inputs)
    x = keras.layers.Dense(max(4, input_dim), activation='relu')(x)
    encoded = keras.layers.Dense(encoding_dim, activation='relu')(x)
    x = keras.layers.Dense(max(4, input_dim), activation='relu')(encoded)
    x = keras.layers.Dense(max(8, input_dim * 2), activation='relu')(x)
    outputs = keras.layers.Dense(input_dim, activation='linear')(x)
    model = keras.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='mse')
    return model


def train_ensemble(df, contamination=0.1, epochs=40, batch_size=32, verbose=0):
    """Train IsolationForest + Autoencoder on engineered features."""
    from sklearn.model_selection import train_test_split

    X, _ = prepare_feature_frame(df)
    if X.shape[0] == 0:
        raise ValueError('No rows available for training.')

    scaler = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    X_scaled = scaler.fit_transform(X)

    iso = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    iso.fit(X_scaled)

    # Try to build and train autoencoder; if TensorFlow isn't available, fall back
    # to an IsolationForest-only ensemble for environments without TF.
    try:
        ae = build_autoencoder(X_scaled.shape[1])
        X_train, X_val = train_test_split(X_scaled, test_size=0.2, random_state=42)
        ae.fit(X_train, X_train, validation_data=(X_val, X_val), epochs=epochs, batch_size=batch_size, verbose=verbose)

        recon = ae.predict(X_scaled, verbose=0)
        recon_err = np.mean(np.square(X_scaled - recon), axis=1)
        iso_score = -iso.score_samples(X_scaled)
        iso_norm = (iso_score - iso_score.min()) / (iso_score.max() - iso_score.min() + 1e-9)
        recon_norm = (recon_err - recon_err.min()) / (recon_err.max() - recon_err.min() + 1e-9)
        ensemble_score = 0.55 * iso_norm + 0.45 * recon_norm
        threshold = float(np.quantile(ensemble_score, 0.90))

        artifacts = EnsembleArtifacts(
            isolation_forest=iso,
            scaler=scaler,
            autoencoder=ae,
            threshold=threshold,
            feature_names=NUMERIC_FEATURES,
        )
    except RuntimeError:
        # TensorFlow unavailable: fall back to IsolationForest-only scoring.
        ae = None
        iso_score = -iso.score_samples(X_scaled)
        iso_norm = (iso_score - iso_score.min()) / (iso_score.max() - iso_score.min() + 1e-9)
        ensemble_score = iso_norm
        threshold = float(np.quantile(ensemble_score, 0.90))
        artifacts = EnsembleArtifacts(
            isolation_forest=iso,
            scaler=scaler,
            autoencoder=None,
            threshold=threshold,
            feature_names=NUMERIC_FEATURES,
        )
    return artifacts, ensemble_score


def save_artifacts(artifacts, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    joblib.dump(artifacts.isolation_forest, os.path.join(out_dir, 'isolation_forest.joblib'))
    joblib.dump(artifacts.scaler, os.path.join(out_dir, 'scaler.joblib'))
    joblib.dump({'threshold': artifacts.threshold, 'feature_names': artifacts.feature_names}, os.path.join(out_dir, 'meta.joblib'))
    # Autoencoder may be None when TF is not available; only save if present.
    if getattr(artifacts, 'autoencoder', None) is not None:
        try:
            artifacts.autoencoder.save(os.path.join(out_dir, 'autoencoder.keras'))
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f'Failed to save autoencoder: {exc}')


def load_artifacts(model_dir):
    iso = joblib.load(os.path.join(model_dir, 'isolation_forest.joblib'))
    scaler = joblib.load(os.path.join(model_dir, 'scaler.joblib'))
    meta = joblib.load(os.path.join(model_dir, 'meta.joblib'))
    autoencoder = None
    ae_path = os.path.join(model_dir, 'autoencoder.keras')
    if os.path.exists(ae_path):
        try:
            tf = _require_tensorflow()
            autoencoder = tf.keras.models.load_model(ae_path)
        except Exception:
            # if TF isn't available, leave autoencoder as None
            autoencoder = None
    return EnsembleArtifacts(
        isolation_forest=iso,
        scaler=scaler,
        autoencoder=autoencoder,
        threshold=meta['threshold'],
        feature_names=meta['feature_names'],
    )


def score_features(artifacts, df):
    X, idx = prepare_feature_frame(df)
    if X.shape[0] == 0:
        return []
    X_scaled = artifacts.scaler.transform(X)
    iso_score = -artifacts.isolation_forest.score_samples(X_scaled)
    iso_norm = (iso_score - iso_score.min()) / (iso_score.max() - iso_score.min() + 1e-9)
    if getattr(artifacts, 'autoencoder', None) is not None:
        recon = artifacts.autoencoder.predict(X_scaled, verbose=0)
        recon_err = np.mean(np.square(X_scaled - recon), axis=1)
        recon_norm = (recon_err - recon_err.min()) / (recon_err.max() - recon_err.min() + 1e-9)
        ensemble_score = 0.55 * iso_norm + 0.45 * recon_norm
    else:
        # fall back to IsolationForest-only scoring
        ensemble_score = iso_norm
        recon_norm = np.zeros_like(iso_norm)
    labels = (ensemble_score >= artifacts.threshold).astype(int)
    return [
        {
            'row_index': int(row_index),
            'score': float(score),
            'is_anomaly': bool(label),
            'iso_score': float(iso),
            'reconstruction_error': float(recon),
        }
        for row_index, score, label, iso, recon in zip(idx, ensemble_score, labels, iso_norm, recon_norm)
    ]
