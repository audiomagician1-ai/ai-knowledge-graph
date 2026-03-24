SELECT 'Starting diagnostics...' AS status;
SELECT count(*) AS profile_count FROM profiles;
SELECT count(*) AS settings_count FROM user_settings;
SELECT count(*) AS auth_users_count FROM auth.users;
SELECT grantee, privilege_type FROM information_schema.table_privileges WHERE table_name = 'profiles' AND table_schema = 'public';