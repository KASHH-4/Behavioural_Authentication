from __future__ import annotations

from typing import Any

from supabase import Client

ALLOWED_EVENT_TYPES = {"mouse_move", "click", "key_down", "key_up"}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sanitize_event(raw_event: dict[str, Any]) -> dict[str, Any] | None:
    event_type = str(raw_event.get("event_type", "")).strip().lower()
    if event_type not in ALLOWED_EVENT_TYPES:
        return None

    timestamp = _to_float(raw_event.get("timestamp"))
    if timestamp is None:
        return None

    return {
        "timestamp": timestamp,
        "event_type": event_type,
        "x": _to_float(raw_event.get("x")),
        "y": _to_float(raw_event.get("y")),
        "dwell_time": _to_float(raw_event.get("dwell_time")),
        "flight_time": _to_float(raw_event.get("flight_time")),
        "inter_event_time": _to_float(raw_event.get("inter_event_time")),
    }


def collect_events(
    session_id: str,
    user_id: str,
    events: list[dict[str, Any]],
    supabase: Client,
    events_table: str,
) -> int:
    stored_count = 0
    payload_rows: list[dict[str, Any]] = []

    for raw_event in events:
        cleaned = sanitize_event(raw_event)
        if cleaned is None:
            continue

        payload_rows.append(
            {
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": cleaned["timestamp"],
                "event_type": cleaned["event_type"],
                "x": cleaned["x"],
                "y": cleaned["y"],
                "dwell_time": cleaned["dwell_time"],
                "flight_time": cleaned["flight_time"],
                "inter_event_time": cleaned["inter_event_time"],
            }
        )
        stored_count += 1

    if payload_rows:
        supabase.table(events_table).insert(payload_rows).execute()

    return stored_count
