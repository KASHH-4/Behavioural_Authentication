from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from app.extensions import get_supabase
from app.services.anomaly_detection import (
    combined_anomaly_score,
    gaussian_distance_score,
    isolation_forest_score,
)
from app.services.data_acquisition import collect_events
from app.services.decision_engine import make_decision
from app.services.feature_extraction import extract_session_features
from app.services.logging_service import log_anomaly, log_prediction, log_session_activity
from app.services.profile_builder import build_profile, get_historical_feature_matrix, upsert_user_profile

api_bp = Blueprint("api", __name__)


def _table(config_key: str) -> str:
    return current_app.config[config_key]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_user(user_id: str) -> None:
    supabase = get_supabase()
    users_table = _table("SUPABASE_USERS_TABLE")
    existing = supabase.table(users_table).select("user_id").eq("user_id", user_id).limit(1).execute().data or []
    if not existing:
        supabase.table(users_table).insert({"user_id": user_id}).execute()


@api_bp.route("/start-session", methods=["POST"])
def start_session():
    payload = request.get_json(silent=True) or {}
    user_id = str(payload.get("user_id", "")).strip()

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        _ensure_user(user_id)
        session_id = str(payload.get("session_id", "")).strip() or str(uuid.uuid4())
        get_supabase().table(_table("SUPABASE_SESSIONS_TABLE")).insert(
            {
                "session_id": session_id,
                "user_id": user_id,
                "start_time": _utc_now_iso(),
            }
        ).execute()
    except Exception as exc:
        return jsonify({"error": "failed to start session", "details": str(exc)}), 500

    log_session_activity(current_app, f"start | user_id={user_id} | session_id={session_id}")
    return jsonify({"session_id": session_id, "user_id": user_id}), 201


@api_bp.route("/end-session", methods=["POST"])
def end_session():
    payload = request.get_json(silent=True) or {}
    session_id = str(payload.get("session_id", "")).strip()

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    supabase = get_supabase()
    sessions_table = _table("SUPABASE_SESSIONS_TABLE")

    session_rows = (
        supabase.table(sessions_table)
        .select("session_id,user_id")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not session_rows:
        return jsonify({"error": "session not found"}), 404
    session_row = session_rows[0]

    try:
        supabase.table(sessions_table).update({"end_time": _utc_now_iso()}).eq("session_id", session_id).execute()
    except Exception as exc:
        return jsonify({"error": "failed to end session", "details": str(exc)}), 500

    log_session_activity(current_app, f"end | user_id={session_row['user_id']} | session_id={session_id}")
    return jsonify({"session_id": session_id, "status": "ended"}), 200


@api_bp.route("/collect", methods=["POST"])
def collect():
    payload = request.get_json(silent=True) or {}
    session_id = str(payload.get("session_id", "")).strip()
    user_id = str(payload.get("user_id", "")).strip()
    events = payload.get("events", [])

    if not session_id or not user_id:
        return jsonify({"error": "session_id and user_id are required"}), 400

    if not isinstance(events, list) or len(events) == 0:
        return jsonify({"error": "events must be a non-empty list"}), 400

    supabase = get_supabase()
    session_rows = (
        supabase.table(_table("SUPABASE_SESSIONS_TABLE"))
        .select("session_id")
        .eq("session_id", session_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not session_rows:
        return jsonify({"error": "session not found for user"}), 404

    try:
        stored_count = collect_events(
            session_id=session_id,
            user_id=user_id,
            events=events,
            supabase=supabase,
            events_table=_table("SUPABASE_EVENTS_TABLE"),
        )
    except Exception as exc:
        return jsonify({"error": "failed to collect events", "details": str(exc)}), 500

    log_session_activity(
        current_app,
        f"collect | user_id={user_id} | session_id={session_id} | stored={stored_count}",
    )
    return jsonify({"stored_events": stored_count}), 201


@api_bp.route("/auth-score", methods=["GET"])
def auth_score():
    session_id = str(request.args.get("session_id", "")).strip()

    if not session_id:
        return jsonify({"error": "session_id query parameter is required"}), 400

    supabase = get_supabase()
    sessions_table = _table("SUPABASE_SESSIONS_TABLE")
    features_table = _table("SUPABASE_FEATURES_TABLE")
    profiles_table = _table("SUPABASE_PROFILES_TABLE")
    results_table = _table("SUPABASE_RESULTS_TABLE")
    events_table = _table("SUPABASE_EVENTS_TABLE")

    try:
        session_rows = (
            supabase.table(sessions_table)
            .select("session_id,user_id")
            .eq("session_id", session_id)
            .limit(1)
            .execute()
            .data
            or []
        )
        if not session_rows:
            return jsonify({"error": "session not found"}), 404
        session = session_rows[0]

        events_rows = (
            supabase.table(events_table)
            .select("timestamp,event_type,x,y,dwell_time,flight_time,inter_event_time")
            .eq("session_id", session_id)
            .order("timestamp", desc=False)
            .execute()
            .data
            or []
        )
        if len(events_rows) < current_app.config["MIN_EVENTS_FOR_SCORING"]:
            return jsonify(
                {
                    "error": "not enough events for scoring",
                    "required": current_app.config["MIN_EVENTS_FOR_SCORING"],
                    "current": len(events_rows),
                }
            ), 400

        raw_features, feature_vector, feature_order = extract_session_features(events_rows)

        supabase.table(features_table).insert(
            {
                "session_id": session_id,
                "user_id": session["user_id"],
                "feature_vector": json.dumps(feature_vector.tolist()),
                "raw_features": json.dumps(raw_features),
                "feature_order": json.dumps(feature_order),
                "created_at": _utc_now_iso(),
            }
        ).execute()

        history = get_historical_feature_matrix(
            user_id=session["user_id"],
            supabase=supabase,
            features_table=features_table,
            exclude_session_id=session_id,
        )
        mean_vec, var_vec, sample_count = build_profile(history)
        upsert_user_profile(
            user_id=session["user_id"],
            feature_order=feature_order,
            mean_vector=mean_vec,
            variance_vector=var_vec,
            sample_count=sample_count,
            supabase=supabase,
            profiles_table=profiles_table,
        )

        gaussian_score = gaussian_distance_score(feature_vector, mean_vec, var_vec)

        if history.size == 0 or history.shape[0] < current_app.config["MIN_HISTORY_FOR_ISOLATION"]:
            iforest_score = 0.5
        else:
            iforest_score = isolation_forest_score(
                feature_vector=feature_vector,
                historical_matrix=history,
                contamination=current_app.config["ISOLATION_CONTAMINATION"],
            )

        combined = combined_anomaly_score(
            gaussian_score,
            iforest_score,
            current_app.config["GAUSSIAN_WEIGHT"],
            current_app.config["IFOR_WEIGHT"],
        )
        decision = make_decision(combined, current_app.config["DECISION_THRESHOLD"])

        details = {
            "sample_count_for_profile": sample_count,
            "model_pipeline": "gaussian_plus_isolation_forest",
        }

        supabase.table(results_table).insert(
            {
                "session_id": session_id,
                "user_id": session["user_id"],
                "timestamp": _utc_now_iso(),
                "gaussian_score": gaussian_score,
                "iforest_score": iforest_score,
                "combined_score": combined,
                "decision": decision,
                "details": json.dumps(details),
            }
        ).execute()
    except Exception as exc:
        return jsonify({"error": "failed to compute auth score", "details": str(exc)}), 500

    msg = (
        f"user_id={session['user_id']} | session_id={session_id} | "
        f"gaussian={gaussian_score:.4f} | iforest={iforest_score:.4f} | "
        f"combined={combined:.4f} | decision={decision}"
    )
    log_prediction(current_app, msg)
    if decision == "Suspicious":
        log_anomaly(current_app, msg)

    return jsonify(
        {
            "session_id": session_id,
            "user_id": session["user_id"],
            "scores": {
                "gaussian": gaussian_score,
                "isolation_forest": iforest_score,
                "combined": combined,
            },
            "decision": decision,
            "threshold": current_app.config["DECISION_THRESHOLD"],
        }
    ), 200
