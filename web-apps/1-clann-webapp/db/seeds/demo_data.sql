-- Demo Data for ClannAI Football Analysis Platform
-- 5 Teams with AI Analysis Results for Meeting Demo

-- Insert demo users (team owners + company users)
INSERT INTO users (id, email, password_hash, name, role) VALUES
  ('11111111-1111-1111-1111-111111111111', 'arsenal@demo.com', '$2b$10$demo_hash_1', 'Arsenal Coach', 'user'),
  ('22222222-2222-2222-2222-222222222222', 'chelsea@demo.com', '$2b$10$demo_hash_2', 'Chelsea Coach', 'user'),
  ('33333333-3333-3333-3333-333333333333', 'liverpool@demo.com', '$2b$10$demo_hash_3', 'Liverpool Coach', 'user'),
  ('44444444-4444-4444-4444-444444444444', 'city@demo.com', '$2b$10$demo_hash_4', 'City Coach', 'user'),
  ('55555555-5555-5555-5555-555555555555', 'united@demo.com', '$2b$10$demo_hash_5', 'United Coach', 'user'),
  ('99999999-9999-9999-9999-999999999999', 'demo@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'Demo User', 'user'),
  ('88888888-8888-8888-8888-888888888888', 'admin@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'ClannAI Admin', 'company'),
  ('77777777-7777-7777-7777-777777777777', 'analyst@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'ClannAI Analyst', 'company');

-- Insert demo teams with join codes
INSERT INTO teams (id, name, description, color, team_code, owner_id, is_public) VALUES
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Arsenal FC Academy', 'Youth team development program', '#FF0000', 'ARS269', '11111111-1111-1111-1111-111111111111', true),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Chelsea Youth', 'Elite youth development squad', '#0000FF', 'CHE277', '22222222-2222-2222-2222-222222222222', true),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Liverpool Reserves', 'Reserve team competitive squad', '#FF0000', 'LIV297', '33333333-3333-3333-3333-333333333333', true),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'City Development', 'Development academy program', '#87CEEB', 'MCI298', '44444444-4444-4444-4444-444444444444', true),
  ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'United U21s', 'Under-21 development team', '#FF0000', 'MUN304', '55555555-5555-5555-5555-555555555555', true);

-- Add team owners as members
INSERT INTO team_members (team_id, user_id) VALUES
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333'),
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', '44444444-4444-4444-4444-444444444444'),
  ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '55555555-5555-5555-5555-555555555555');

-- Insert demo games with AI analysis results
-- Game 1: Arsenal FC Academy (Game269_0511)
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('11111111-1269-0511-0000-000000000000', 
   'Arsenal vs Local Academy - May 11th', 
   'Competitive youth match with tactical focus',
   'https://demo-videos.clann.ai/game269_0511.mp4',
   'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
   '11111111-1111-1111-1111-111111111111',
   'analyzed',
   5400, -- 90 minutes
   '{"total_events": 45, "goals": 3, "shots": 18, "saves": 8, "analysis_date": "2025-07-24T16:44:28", "event_types": {"shot_on_target": 18, "goalkeeper_save": 8, "goal": 3, "turnover": 12, "major_foul": 4}}'::jsonb);

-- Game 2: Chelsea Youth (Game277_0526)  
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('22222222-2277-0526-0000-000000000000',
   'Chelsea Youth vs Brighton Academy - May 26th',
   'High-intensity academy match',
   'https://demo-videos.clann.ai/game277_0526.mp4', 
   'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
   '22222222-2222-2222-2222-222222222222',
   'analyzed',
   5400,
   '{"total_events": 52, "goals": 2, "shots": 24, "saves": 11, "analysis_date": "2025-07-24T16:44:28", "event_types": {"shot_on_target": 24, "goalkeeper_save": 11, "goal": 2, "turnover": 10, "major_foul": 5}}'::jsonb);

-- Game 3: Liverpool Reserves (Game297_0616)
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('33333333-3297-0616-0000-000000000000',
   'Liverpool Reserves vs Everton U21 - June 16th',
   'Merseyside derby at reserve level',
   'https://demo-videos.clann.ai/game297_0616.mp4',
   'cccccccc-cccc-cccc-cccc-cccccccccccc', 
   '33333333-3333-3333-3333-333333333333',
   'analyzed',
   5400,
   '{"total_events": 67, "goals": 4, "shots": 31, "saves": 20, "analysis_date": "2025-07-24T16:44:28", "event_types": {"shot_on_target": 31, "goalkeeper_save": 20, "goal": 4, "turnover": 7, "major_foul": 5}}'::jsonb);

-- Game 4: City Development (Game298_0601)
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('44444444-4298-0601-0000-000000000000',
   'City Development vs Newcastle Academy - June 1st',
   'Development squad friendly',
   'https://demo-videos.clann.ai/game298_0601.mp4',
   'dddddddd-dddd-dddd-dddd-dddddddddddd',
   '44444444-4444-4444-4444-444444444444', 
   'analyzed',
   917, -- 15 minutes (shorter game)
   '{"total_events": 49, "goals": 2, "shots": 33, "saves": 14, "analysis_date": "2025-07-24T16:44:28", "event_types": {"shot_on_target": 33, "goalkeeper_save": 14, "goal": 2, "turnover": 0, "major_foul": 0}}'::jsonb);

-- Game 5: United U21s (Game304_0618)
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('55555555-5304-0618-0000-000000000000',
   'United U21s vs Tottenham Development - June 18th', 
   'Competitive U21 league match',
   'https://demo-videos.clann.ai/game304_0618.mp4',
   'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
   '55555555-5555-5555-5555-555555555555',
   'analyzed', 
   5400,
   '{"total_events": 58, "goals": 3, "shots": 28, "saves": 15, "analysis_date": "2025-07-24T16:44:28", "event_types": {"shot_on_target": 28, "goalkeeper_save": 15, "goal": 3, "turnover": 8, "major_foul": 4}}'::jsonb);

-- Add some pending games to demonstrate company workflow
INSERT INTO games (id, title, description, video_url, team_id, uploaded_by, status, duration) VALUES
  ('66666666-6666-6666-6666-666666666601',
   'Arsenal vs Brighton - July 28th',
   'Recent match awaiting analysis',
   'https://veo.co/watch/demo-match-arsenal-brighton',
   'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
   '11111111-1111-1111-1111-111111111111',
   'pending',
   5400),
  ('77777777-7777-7777-7777-777777777702',
   'Chelsea vs Southampton - July 27th', 
   'Latest academy match for processing',
   'https://veo.co/watch/demo-match-chelsea-southampton',
   'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
   '22222222-2222-2222-2222-222222222222',
   'pending',
   5400);

-- Verify data inserted
SELECT 'Demo data loaded successfully!' as message;
SELECT COUNT(*) || ' users created' as users_count FROM users;
SELECT COUNT(*) || ' teams created' as teams_count FROM teams;  
SELECT COUNT(*) || ' games created' as games_count FROM games;

-- Show user roles for demo
SELECT 
  role,
  COUNT(*) as count,
  string_agg(name, ', ') as users
FROM users 
GROUP BY role 
ORDER BY role;

-- Show game statuses for demo  
SELECT 
  status,
  COUNT(*) as count
FROM games
GROUP BY status
ORDER BY status;

-- Display team codes for demo
SELECT name, team_code, 'Join this team using code: ' || team_code as instruction 
FROM teams 
ORDER BY name; 