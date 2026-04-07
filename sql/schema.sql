CREATE TABLE users (
    user_id VARCHAR(64) PRIMARY KEY
);

CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE raw_behavior_data (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    x DOUBLE PRECISION,
    y DOUBLE PRECISION,
    dwell_time DOUBLE PRECISION,
    flight_time DOUBLE PRECISION,
    inter_event_time DOUBLE PRECISION,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE features (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    feature_vector TEXT NOT NULL,
    raw_features TEXT NOT NULL,
    feature_order TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL UNIQUE,
    mean_vector TEXT NOT NULL,
    variance_vector TEXT NOT NULL,
    feature_order TEXT NOT NULL,
    sample_count INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE results (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    gaussian_score DOUBLE PRECISION NOT NULL,
    iforest_score DOUBLE PRECISION NOT NULL,
    combined_score DOUBLE PRECISION NOT NULL,
    decision VARCHAR(32) NOT NULL,
    details TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_events_session_id ON raw_behavior_data(session_id);
CREATE INDEX idx_events_user_id ON raw_behavior_data(user_id);
CREATE INDEX idx_events_timestamp ON raw_behavior_data(timestamp);
CREATE INDEX idx_features_user_id ON features(user_id);
CREATE INDEX idx_results_session_id ON results(session_id);
