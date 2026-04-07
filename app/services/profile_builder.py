from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
from supabase import Client


def _decode_vector(raw: str | list[float]) -> np.ndarray:
    values = json.loads(raw) if isinstance(raw, str) else raw
    return np.array(values, dtype=float)


def get_historical_feature_matrix(
    user_id: str,
    supabase: Client,
    features_table: str,
    exclude_session_id: str | None = None,
) -> np.ndarray:
    query = supabase.table(features_table).select("feature_vector").eq("user_id", user_id).order("created_at", desc=False)
    if exclude_session_id:
        query = query.neq("session_id", exclude_session_id)

    rows = query.execute().data or []
    if not rows:
        return np.empty((0, 0))

    matrix = [_decode_vector(row["feature_vector"]) for row in rows]
    return np.vstack(matrix)


def build_profile(feature_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    if feature_matrix.size == 0:
        return np.array([]), np.array([]), 0

    mean_vector = np.mean(feature_matrix, axis=0)
    variance_vector = np.var(feature_matrix, axis=0) + 1e-6
    sample_count = int(feature_matrix.shape[0])
    return mean_vector, variance_vector, sample_count


def upsert_user_profile(
    user_id: str,
    feature_order: list[str],
    mean_vector: np.ndarray,
    variance_vector: np.ndarray,
    sample_count: int,
    supabase: Client,
    profiles_table: str,
) -> dict | None:
    if sample_count == 0:
        return None

    payload = {
        "user_id": user_id,
        "mean_vector": json.dumps(mean_vector.tolist()),
        "variance_vector": json.dumps(variance_vector.tolist()),
        "feature_order": json.dumps(feature_order),
        "sample_count": sample_count,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    response = supabase.table(profiles_table).upsert(payload, on_conflict="user_id").execute()
    return (response.data or [None])[0]
