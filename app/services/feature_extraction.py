from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_ORDER = [
    "mouse_velocity_mean",
    "mouse_velocity_std",
    "mouse_velocity_max",
    "mouse_acceleration_mean",
    "mouse_acceleration_std",
    "mouse_acceleration_max",
    "mouse_direction_changes",
    "click_interval_mean",
    "click_interval_std",
    "typing_speed",
    "dwell_time_mean",
    "dwell_time_std",
    "flight_time_mean",
    "flight_time_std",
    "interaction_interval_mean",
    "interaction_interval_std",
    "event_rate",
    "total_events",
]


def _safe_series(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce")
    return pd.Series(dtype=float)


def _vectorize(features: dict[str, float]) -> np.ndarray:
    vector = np.array([float(features.get(name, 0.0)) for name in FEATURE_ORDER], dtype=float)
    vector = np.nan_to_num(vector, nan=0.0, posinf=0.0, neginf=0.0)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector


def extract_session_features(events: list[dict]) -> tuple[dict[str, float], np.ndarray, list[str]]:
    if not events:
        zero_features = {name: 0.0 for name in FEATURE_ORDER}
        return zero_features, _vectorize(zero_features), FEATURE_ORDER

    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_numeric(df.get("timestamp"), errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)

    features = {name: 0.0 for name in FEATURE_ORDER}

    timestamps = df["timestamp"].to_numpy(dtype=float)
    duration = float(max(timestamps[-1] - timestamps[0], 1e-6))
    features["total_events"] = float(len(df))
    features["event_rate"] = float(len(df) / duration)

    mouse_df = df[(df["event_type"] == "mouse_move") | (df["event_type"] == "click")].copy()
    if len(mouse_df) >= 2:
        x = pd.to_numeric(mouse_df.get("x"), errors="coerce").to_numpy(dtype=float)
        y = pd.to_numeric(mouse_df.get("y"), errors="coerce").to_numpy(dtype=float)
        t = pd.to_numeric(mouse_df.get("timestamp"), errors="coerce").to_numpy(dtype=float)

        valid = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(t)
        x, y, t = x[valid], y[valid], t[valid]

        if len(t) >= 2:
            dx = np.diff(x)
            dy = np.diff(y)
            dt = np.maximum(np.diff(t), 1e-6)
            dist = np.sqrt(dx ** 2 + dy ** 2)
            velocity = dist / dt

            features["mouse_velocity_mean"] = float(np.mean(velocity))
            features["mouse_velocity_std"] = float(np.std(velocity))
            features["mouse_velocity_max"] = float(np.max(velocity))

            if len(velocity) >= 2:
                acceleration = np.diff(velocity) / np.maximum(dt[1:], 1e-6)
                features["mouse_acceleration_mean"] = float(np.mean(acceleration))
                features["mouse_acceleration_std"] = float(np.std(acceleration))
                features["mouse_acceleration_max"] = float(np.max(np.abs(acceleration)))

            angles = np.arctan2(dy, dx)
            if len(angles) >= 2:
                angle_change = np.abs(np.diff(angles))
                features["mouse_direction_changes"] = float(np.sum(angle_change > (np.pi / 4)))

    click_df = df[df["event_type"] == "click"]
    if len(click_df) >= 2:
        click_times = click_df["timestamp"].to_numpy(dtype=float)
        click_intervals = np.diff(click_times)
        features["click_interval_mean"] = float(np.mean(click_intervals))
        features["click_interval_std"] = float(np.std(click_intervals))

    key_down_df = df[df["event_type"] == "key_down"]
    if len(key_down_df) > 0:
        features["typing_speed"] = float(len(key_down_df) / duration)

    dwell = _safe_series(df, "dwell_time").dropna().to_numpy(dtype=float)
    if len(dwell) > 0:
        features["dwell_time_mean"] = float(np.mean(dwell))
        features["dwell_time_std"] = float(np.std(dwell))

    flight = _safe_series(df, "flight_time").dropna().to_numpy(dtype=float)
    if len(flight) > 0:
        features["flight_time_mean"] = float(np.mean(flight))
        features["flight_time_std"] = float(np.std(flight))

    inter = _safe_series(df, "inter_event_time").dropna().to_numpy(dtype=float)
    if len(inter) == 0 and len(timestamps) >= 2:
        inter = np.diff(timestamps)
    if len(inter) > 0:
        features["interaction_interval_mean"] = float(np.mean(inter))
        features["interaction_interval_std"] = float(np.std(inter))

    feature_vector = _vectorize(features)
    return features, feature_vector, FEATURE_ORDER
