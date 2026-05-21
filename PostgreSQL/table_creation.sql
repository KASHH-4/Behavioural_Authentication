-- =========================================
-- USERS
-- =========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    external_user_id TEXT UNIQUE NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);





-- =========================================
-- SESSIONS
-- =========================================

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES users(id)
    ON DELETE CASCADE,

    start_time TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,

    is_active BOOLEAN DEFAULT TRUE,
    is_valid BOOLEAN DEFAULT TRUE,

    invalid_reason TEXT,

    batch_count INT DEFAULT 0,

    -- FINAL AGGREGATED FEATURES
    avg_dwell_time DOUBLE PRECISION,
    std_dwell_time DOUBLE PRECISION,

    avg_flight_time DOUBLE PRECISION,
    std_flight_time DOUBLE PRECISION,

    avg_inter_event_time DOUBLE PRECISION,
    std_inter_event_time DOUBLE PRECISION,

    avg_speed DOUBLE PRECISION,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_active_lastseen
ON sessions(is_active, last_seen);

CREATE INDEX idx_sessions_active_only
ON sessions(last_seen)
WHERE is_active = TRUE;





-- =========================================
-- SESSION BATCHES
-- =========================================

CREATE TABLE session_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    session_id UUID NOT NULL REFERENCES sessions(session_id)
    ON DELETE CASCADE,

    user_id UUID NOT NULL REFERENCES users(id)
    ON DELETE CASCADE,

    batch_start TIMESTAMPTZ NOT NULL,
    batch_end TIMESTAMPTZ NOT NULL,

    -- FEATURE VECTOR
    avg_dwell_time DOUBLE PRECISION,
    std_dwell_time DOUBLE PRECISION,

    avg_flight_time DOUBLE PRECISION,
    std_flight_time DOUBLE PRECISION,

    avg_inter_event_time DOUBLE PRECISION,
    std_inter_event_time DOUBLE PRECISION,

    avg_speed DOUBLE PRECISION,

    event_count INT,

    is_anomalous BOOLEAN DEFAULT FALSE NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_batch_time
    CHECK(batch_end > batch_start)
);

CREATE UNIQUE INDEX ux_batch_window
ON session_batches(session_id, batch_start, batch_end);

CREATE INDEX idx_batches_session
ON session_batches(session_id);

CREATE INDEX idx_batches_active
ON session_batches(session_id, created_at);

CREATE INDEX idx_batches_anomalous
ON session_batches(session_id)
WHERE is_anomalous = TRUE;





-- =========================================
-- USER PROFILES
-- =========================================

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id)
    ON DELETE CASCADE,

    mean_vector JSONB NOT NULL,

    variance_vector JSONB NOT NULL,

    sample_count INT DEFAULT 0,

    updated_at TIMESTAMPTZ DEFAULT NOW()
);





-- =========================================
-- RESULTS
-- =========================================

CREATE TABLE results (
    id BIGSERIAL PRIMARY KEY,

    batch_id UUID NOT NULL REFERENCES session_batches(batch_id)
    ON DELETE CASCADE,

    session_id UUID NOT NULL REFERENCES sessions(session_id)
    ON DELETE CASCADE,

    user_id UUID NOT NULL REFERENCES users(id)
    ON DELETE CASCADE,

    gaussian_score DOUBLE PRECISION,

    iforest_score DOUBLE PRECISION,

    combined_score DOUBLE PRECISION,

    decision TEXT NOT NULL,

    details JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_results_batch
ON results(batch_id);

CREATE INDEX idx_results_session
ON results(session_id);