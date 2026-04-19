-- Users table
CREATE TABLE users (
  site_id UUID NOT NULL,
  user_id UUID NOT NULL,
  PRIMARY KEY (site_id, user_id)
);


-- Sessions (core table)
CREATE TABLE sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  user_id UUID NOT NULL,

  start_time TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  end_time TIMESTAMPTZ,

  is_active BOOLEAN DEFAULT TRUE,
  is_valid BOOLEAN DEFAULT TRUE,
  invalid_reason TEXT,
  batch_count INT DEFAULT 0,

  -- FINAL AGGREGATED FEATURES (computed at end)
  avg_dwell_time DOUBLE PRECISION,
  std_dwell_time DOUBLE PRECISION,
  avg_flight_time DOUBLE PRECISION,
  std_flight_time DOUBLE PRECISION,
  avg_inter_event_time DOUBLE PRECISION,
  std_inter_event_time DOUBLE PRECISION,
  avg_speed DOUBLE PRECISION,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  FOREIGN KEY (site_id, user_id)
    REFERENCES users(site_id, user_id)
);

ALTER TABLE sessions
ADD CONSTRAINT unique_session_user
UNIQUE (session_id, site_id, user_id);

CREATE INDEX idx_sessions_expiry
ON sessions (end_time)
WHERE is_active = TRUE;




--SESSION BATCHES (TEMPORARY WORKING DATA)
CREATE TABLE session_batches (
  batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL,
  site_id UUID NOT NULL,
  user_id UUID NOT NULL,

  batch_start TIMESTAMPTZ NOT NULL,
  batch_end TIMESTAMPTZ NOT NULL,

  -- FEATURE VECTOR (per 30 sec window)
  avg_dwell_time DOUBLE PRECISION,
  std_dwell_time DOUBLE PRECISION,
  avg_flight_time DOUBLE PRECISION,
  std_flight_time DOUBLE PRECISION,
  avg_inter_event_time DOUBLE PRECISION,
  std_inter_event_time DOUBLE PRECISION,
  avg_speed DOUBLE PRECISION,

  event_count INT,
  -- quick flag (optional optimization)
  is_anomalous BOOLEAN DEFAULT FALSE NOT NULL,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (session_id, site_id, user_id)
    REFERENCES sessions(session_id, site_id, user_id)
    ON DELETE CASCADE
);

CREATE UNIQUE INDEX ux_batch_window
ON session_batches (session_id, batch_start, batch_end);

ALTER TABLE session_batches
ADD CONSTRAINT chk_batch_time
CHECK (batch_end > batch_start);




-- User_profile (baseline for the model)
CREATE TABLE user_profiles (
  site_id UUID NOT NULL,
  user_id UUID NOT NULL,

  mean_vector JSONB NOT NULL,
  variance_vector JSONB NOT NULL,

  sample_count INT DEFAULT 0,

  updated_at TIMESTAMPTZ DEFAULT NOW(),

  PRIMARY KEY (site_id, user_id),

  FOREIGN KEY (site_id, user_id)
    REFERENCES users(site_id, user_id)
    ON DELETE CASCADE
);




-- Results (Model-output per-batch)
CREATE TABLE results (
  id BIGSERIAL PRIMARY KEY,
  batch_id UUID NOT NULL,
  session_id UUID NOT NULL,

  site_id UUID NOT NULL,
  user_id UUID NOT NULL,

  created_at TIMESTAMPTZ DEFAULT NOW(),

  gaussian_score DOUBLE PRECISION,
  iforest_score DOUBLE PRECISION,
  combined_score DOUBLE PRECISION,

  decision TEXT NOT NULL,
  details JSONB,

  FOREIGN KEY (batch_id)
    REFERENCES session_batches(batch_id)
    ON DELETE CASCADE,
  FOREIGN KEY (session_id, site_id, user_id)
    REFERENCES sessions(session_id, site_id, user_id)
    ON DELETE CASCADE
);







-- Indexes
-- session expiry (cron)
CREATE INDEX idx_sessions_active_lastseen
ON sessions (is_active, last_seen);


-- batch lookup
CREATE INDEX idx_batches_session
ON session_batches (session_id);
CREATE INDEX idx_batches_active
ON session_batches (session_id, created_at);

-- results lookup
CREATE INDEX idx_results_batch
ON results (batch_id);

CREATE INDEX idx_results_session
ON results (session_id);

CREATE INDEX idx_sessions_active_only
ON sessions (last_seen)
WHERE is_active = TRUE;

CREATE INDEX idx_batches_anomalous
ON session_batches (session_id)
WHERE is_anomalous = TRUE;