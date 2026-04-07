from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest


def gaussian_distance_score(
    feature_vector: np.ndarray,
    mean_vector: np.ndarray,
    variance_vector: np.ndarray,
) -> float:
    if feature_vector.size == 0 or mean_vector.size == 0 or variance_vector.size == 0:
        return 0.5

    z = (feature_vector - mean_vector) / np.sqrt(variance_vector + 1e-6)
    distance = float(np.sqrt(np.mean(z ** 2)))
    score = 1.0 - np.exp(-distance)
    return float(np.clip(score, 0.0, 1.0))


def isolation_forest_score(
    feature_vector: np.ndarray,
    historical_matrix: np.ndarray,
    contamination: float,
) -> float:
    if feature_vector.size == 0 or historical_matrix.size == 0:
        return 0.5

    if historical_matrix.ndim != 2 or historical_matrix.shape[0] < 2:
        return 0.5

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    model.fit(historical_matrix)

    decision = float(model.decision_function(feature_vector.reshape(1, -1))[0])
    # Lower decision_function indicates anomaly; convert to [0, 1].
    anomaly_score = 1.0 / (1.0 + np.exp(5.0 * decision))
    return float(np.clip(anomaly_score, 0.0, 1.0))


def combined_anomaly_score(gaussian_score: float, iforest_score: float, gw: float, iw: float) -> float:
    total = max(gw + iw, 1e-6)
    combined = (gaussian_score * gw + iforest_score * iw) / total
    return float(np.clip(combined, 0.0, 1.0))
