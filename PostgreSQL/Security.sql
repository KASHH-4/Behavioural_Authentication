ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON users FROM anon;
REVOKE ALL ON sessions FROM anon;
REVOKE ALL ON session_batches FROM anon;
REVOKE ALL ON user_profiles FROM anon;
REVOKE ALL ON results FROM anon;

GRANT SELECT, INSERT, UPDATE ON users TO authenticated;
GRANT SELECT, INSERT, UPDATE ON sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON session_batches TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON results TO authenticated;



-- Policies
-- Users
CREATE POLICY "users_self_access"
ON users
FOR ALL
USING (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
)
WITH CHECK (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
);


-- Sessions
CREATE POLICY "sessions_self_access"
ON sessions
FOR ALL
USING (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
)
WITH CHECK (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
);


-- Session Batches
CREATE POLICY "batches_self_access"
ON session_batches
FOR ALL
USING (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
)
WITH CHECK (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
);


-- User Profiles
CREATE POLICY "profiles_self_access"
ON user_profiles
FOR ALL
USING (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
)
WITH CHECK (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
);


-- results
CREATE POLICY "results_self_access"
ON results
FOR ALL
USING (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
)
WITH CHECK (
  site_id = (auth.jwt() ->> 'site_id')::uuid
  AND user_id = (auth.jwt() ->> 'user_id')::uuid
);