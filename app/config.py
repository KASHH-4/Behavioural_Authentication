import os


class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    SUPABASE_USERS_TABLE = os.getenv("SUPABASE_USERS_TABLE", "users")
    SUPABASE_SESSIONS_TABLE = os.getenv("SUPABASE_SESSIONS_TABLE", "sessions")
    SUPABASE_EVENTS_TABLE = os.getenv("SUPABASE_EVENTS_TABLE", "raw_behavior_data")
    SUPABASE_FEATURES_TABLE = os.getenv("SUPABASE_FEATURES_TABLE", "features")
    SUPABASE_PROFILES_TABLE = os.getenv("SUPABASE_PROFILES_TABLE", "user_profiles")
    SUPABASE_RESULTS_TABLE = os.getenv("SUPABASE_RESULTS_TABLE", "results")

    DECISION_THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.60"))
    GAUSSIAN_WEIGHT = float(os.getenv("GAUSSIAN_WEIGHT", "0.50"))
    IFOR_WEIGHT = float(os.getenv("IFOR_WEIGHT", "0.50"))

    MIN_EVENTS_FOR_SCORING = int(os.getenv("MIN_EVENTS_FOR_SCORING", "10"))
    MIN_HISTORY_FOR_ISOLATION = int(os.getenv("MIN_HISTORY_FOR_ISOLATION", "5"))
    ISOLATION_CONTAMINATION = float(os.getenv("ISOLATION_CONTAMINATION", "0.10"))
