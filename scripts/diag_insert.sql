INSERT INTO auth.users (
  id, instance_id, aud, role, email, encrypted_password, 
  email_confirmed_at, raw_app_meta_data, raw_user_meta_data, 
  created_at, updated_at, is_sso_user, is_anonymous
) VALUES (
  gen_random_uuid(), '00000000-0000-0000-0000-000000000000', 'authenticated', 'authenticated',
  'diagtest@example.com', crypt('TestPass123456', gen_salt('bf')),
  now(), '{"provider":"email","providers":["email"]}'::jsonb,
  '{"display_name":"DiagTest"}'::jsonb,
  now(), now(), false, false
);