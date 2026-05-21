-- =========================================
-- ENABLE RLS
-- =========================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;





-- =========================================
-- DEVELOPMENT POLICIES
-- =========================================

CREATE POLICY "allow_all_users"
ON users
FOR ALL
USING (TRUE)
WITH CHECK (TRUE);

CREATE POLICY "allow_all_sessions"
ON sessions
FOR ALL
USING (TRUE)
WITH CHECK (TRUE);

CREATE POLICY "allow_all_batches"
ON session_batches
FOR ALL
USING (TRUE)
WITH CHECK (TRUE);

CREATE POLICY "allow_all_profiles"
ON user_profiles
FOR ALL
USING (TRUE)
WITH CHECK (TRUE);

CREATE POLICY "allow_all_results"
ON results
FOR ALL
USING (TRUE)
WITH CHECK (TRUE);