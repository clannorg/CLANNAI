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
-- Game 1: Arsenal FC Academy (Game269_0511) - Updated with detailed event timeline
INSERT INTO games (id, title, description, video_url, s3_key, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('11111111-1269-0511-0000-000000000000', 
   'Arsenal vs Local Academy - May 11th', 
   'Competitive youth match with tactical focus',
   'https://veo.co/watch/demo-match-arsenal-academy',
   'games/arsenal-academy/full-game.mp4',
   'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
   '11111111-1111-1111-1111-111111111111',
   'analyzed',
   5400, -- 90 minutes
   '[
     {"type": "shot", "timestamp": 37, "description": "Shot on goal", "player": "Smith #9"},
     {"type": "goal", "timestamp": 37, "description": "Goal scored", "player": "Smith #9"},
     {"type": "shot", "timestamp": 269, "description": "Shot on goal", "player": "Jones #11"},
     {"type": "shot", "timestamp": 559, "description": "Shot on goal", "player": "Wilson #7"},
     {"type": "shot", "timestamp": 769, "description": "Shot on goal", "player": "Brown #10"},
     {"type": "goal", "timestamp": 771, "description": "Goal scored", "player": "Brown #10"},
     {"type": "shot", "timestamp": 876, "description": "Shot on goal", "player": "Davis #8"},
     {"type": "foul", "timestamp": 1200, "description": "Defensive foul", "player": "Miller #3"},
     {"type": "yellow_card", "timestamp": 1205, "description": "Cautioned for foul", "player": "Miller #3"},
     {"type": "shot", "timestamp": 1893, "description": "Shot on goal", "player": "Taylor #6"},
     {"type": "corner", "timestamp": 2100, "description": "Corner kick", "player": "Wilson #7"},
     {"type": "shot", "timestamp": 2199, "description": "Shot on goal", "player": "Evans #5"},
     {"type": "shot", "timestamp": 2282, "description": "Shot on goal", "player": "Johnson #4"},
     {"type": "substitution", "timestamp": 2700, "description": "Player substitution", "player": "Rodriguez #12 for Smith #9"},
     {"type": "shot", "timestamp": 3575, "description": "Shot on goal", "player": "Anderson #14"},
     {"type": "shot", "timestamp": 3986, "description": "Shot on goal", "player": "Thomas #13"},
     {"type": "shot", "timestamp": 4075, "description": "Shot on goal", "player": "Lee #15"},
     {"type": "goal", "timestamp": 4075, "description": "Goal scored", "player": "Lee #15"},
     {"type": "shot", "timestamp": 4594, "description": "Shot on goal", "player": "Garcia #16"},
     {"type": "shot", "timestamp": 5160, "description": "Shot on goal", "player": "Martinez #17"},
     {"type": "shot", "timestamp": 5227, "description": "Shot on goal", "player": "Lopez #18"},
     {"type": "shot", "timestamp": 5786, "description": "Shot on goal", "player": "Clark #19"},
     {"type": "goal", "timestamp": 5788, "description": "Goal scored", "player": "Clark #19"},
     {"type": "shot", "timestamp": 6240, "description": "Shot on goal", "player": "White #20"}
   ]'::jsonb);

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
   '[
     {"type": "shot", "timestamp": 67, "description": "Early pressure shot", "player": "Mount #19", "team": "blue"},
     {"type": "goal", "timestamp": 69, "description": "Clinical finish", "player": "Mount #19", "team": "blue"},
     {"type": "shot", "timestamp": 234, "description": "Counter attack shot", "player": "Hudson-Odoi #20", "team": "blue"},
     {"type": "save", "timestamp": 236, "description": "Goalkeeper save", "player": "Steele #1", "team": "red"},
     {"type": "corner", "timestamp": 420, "description": "Corner kick", "player": "James #24", "team": "blue"},
     {"type": "shot", "timestamp": 465, "description": "Header from corner", "player": "Chalobah #14", "team": "blue"},
     {"type": "foul", "timestamp": 890, "description": "Midfield challenge", "player": "Gallagher #23", "team": "blue"},
     {"type": "yellow_card", "timestamp": 895, "description": "Caution for foul", "player": "Gallagher #23", "team": "blue"},
     {"type": "shot", "timestamp": 1234, "description": "Free kick attempt", "player": "Reece #24", "team": "blue"},
     {"type": "substitution", "timestamp": 2700, "description": "Fresh legs", "player": "Broja #18 for Mount #19", "team": "blue"},
     {"type": "shot", "timestamp": 3456, "description": "Late shot", "player": "Broja #18", "team": "blue"},
     {"type": "goal", "timestamp": 3458, "description": "Sealed the win", "player": "Broja #18", "team": "blue"}
   ]'::jsonb);

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
   '[
     {"type": "shot", "timestamp": 45, "description": "Derby opener", "player": "Salah Jr #11", "team": "red"},
     {"type": "goal", "timestamp": 47, "description": "Liverpool strikes first", "player": "Salah Jr #11", "team": "red"},
     {"type": "foul", "timestamp": 123, "description": "Tough tackle", "player": "Gordon #7", "team": "black"},
     {"type": "yellow_card", "timestamp": 125, "description": "Derby intensity", "player": "Gordon #7", "team": "black"},
     {"type": "shot", "timestamp": 289, "description": "Everton response", "player": "Gordon #7", "team": "black"},
     {"type": "goal", "timestamp": 291, "description": "Equalizer", "player": "Gordon #7", "team": "black"},
     {"type": "shot", "timestamp": 567, "description": "Liverpool pressure", "player": "Elliott #19", "team": "red"},
     {"type": "save", "timestamp": 569, "description": "Great save", "player": "Pickford Jr #1", "team": "black"},
     {"type": "corner", "timestamp": 890, "description": "Corner kick", "player": "Robertson Jr #26", "team": "red"},
     {"type": "shot", "timestamp": 920, "description": "Header chance", "player": "Van Dijk Jr #4", "team": "red"},
     {"type": "goal", "timestamp": 922, "description": "Liverpool lead", "player": "Van Dijk Jr #4", "team": "red"},
     {"type": "substitution", "timestamp": 2700, "description": "Tactical change", "player": "Calvert-Lewin Jr #9 for Gordon #7", "team": "black"},
     {"type": "shot", "timestamp": 3245, "description": "Late equalizer attempt", "player": "Calvert-Lewin Jr #9", "team": "black"},
     {"type": "goal", "timestamp": 3247, "description": "Derby drama", "player": "Calvert-Lewin Jr #9", "team": "black"},
     {"type": "shot", "timestamp": 4567, "description": "Winner attempt", "player": "Nunez Jr #27", "team": "red"},
     {"type": "goal", "timestamp": 4569, "description": "Liverpool wins derby", "player": "Nunez Jr #27", "team": "red"}
   ]'::jsonb);

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
   '[
     {"type": "shot", "timestamp": 34, "description": "Early chance", "player": "Foden Jr #47", "team": "blue"},
     {"type": "shot", "timestamp": 67, "description": "Quick follow up", "player": "Palmer #80", "team": "blue"},
     {"type": "goal", "timestamp": 69, "description": "City takes lead", "player": "Palmer #80", "team": "blue"},
     {"type": "shot", "timestamp": 145, "description": "Newcastle response", "player": "Isak Jr #14", "team": "black"},
     {"type": "save", "timestamp": 147, "description": "Keeper denies", "player": "Ortega #18", "team": "blue"},
     {"type": "corner", "timestamp": 234, "description": "Corner to Newcastle", "player": "Bruno Jr #39", "team": "black"},
     {"type": "shot", "timestamp": 267, "description": "Header from corner", "player": "Burn Jr #33", "team": "black"},
     {"type": "goal", "timestamp": 269, "description": "Newcastle equalizes", "player": "Burn Jr #33", "team": "black"},
     {"type": "shot", "timestamp": 456, "description": "City counter", "player": "Alvarez #19", "team": "blue"},
     {"type": "shot", "timestamp": 567, "description": "Long range effort", "player": "De Bruyne Jr #17", "team": "blue"},
     {"type": "substitution", "timestamp": 600, "description": "Fresh legs", "player": "Haaland Jr #9 for Alvarez #19", "team": "blue"},
     {"type": "shot", "timestamp": 789, "description": "Haaland chance", "player": "Haaland Jr #9", "team": "blue"},
     {"type": "goal", "timestamp": 791, "description": "Winner from Haaland", "player": "Haaland Jr #9", "team": "blue"}
   ]'::jsonb);

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
   '[
     {"type": "shot", "timestamp": 89, "description": "United pressure", "player": "Rashford Jr #10", "team": "red"},
     {"type": "goal", "timestamp": 91, "description": "Early United goal", "player": "Rashford Jr #10", "team": "red"},
     {"type": "foul", "timestamp": 234, "description": "Tough challenge", "player": "Romero Jr #17", "team": "black"},
     {"type": "yellow_card", "timestamp": 236, "description": "Booked for foul", "player": "Romero Jr #17", "team": "black"},
     {"type": "shot", "timestamp": 567, "description": "Spurs response", "player": "Kane Jr #9", "team": "black"},
     {"type": "save", "timestamp": 569, "description": "De Gea Jr save", "player": "De Gea Jr #1", "team": "red"},
     {"type": "corner", "timestamp": 890, "description": "Spurs corner", "player": "Son Jr #7", "team": "black"},
     {"type": "shot", "timestamp": 923, "description": "Header chance", "player": "Kane Jr #9", "team": "black"},
     {"type": "goal", "timestamp": 925, "description": "Spurs equalizer", "player": "Kane Jr #9", "team": "black"},
     {"type": "substitution", "timestamp": 2700, "description": "Tactical switch", "player": "Antony Jr #21 for Sancho Jr #25", "team": "red"},
     {"type": "shot", "timestamp": 3456, "description": "United chance", "player": "Antony Jr #21", "team": "red"},
     {"type": "shot", "timestamp": 4123, "description": "Late pressure", "player": "Martial Jr #9", "team": "red"},
     {"type": "goal", "timestamp": 4125, "description": "United winner", "player": "Martial Jr #9", "team": "red"}
   ]'::jsonb);

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

-- Test Game with Working Video URL for immediate testing
INSERT INTO games (id, title, description, video_url, s3_key, team_id, uploaded_by, status, duration, ai_analysis) VALUES
  ('99999999-9999-9999-9999-999999999999',
   'Demo Video - Test Video Player', 
   'Test game with working video for video player testing',
   'https://veo.co/watch/demo-test',
   'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
   'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
   '11111111-1111-1111-1111-111111111111',
   'analyzed',
   596, -- ~10 minutes  
   '[
     {"type": "shot", "timestamp": 15, "description": "Early shot attempt", "player": "Bunny #1"},
     {"type": "goal", "timestamp": 17, "description": "Opening goal", "player": "Bunny #1"},
     {"type": "foul", "timestamp": 45, "description": "Defensive challenge", "player": "Rodent #3"},
     {"type": "yellow_card", "timestamp": 47, "description": "Caution for rough play", "player": "Rodent #3"},
     {"type": "shot", "timestamp": 120, "description": "Long range effort", "player": "Squirrel #7"},
     {"type": "corner", "timestamp": 180, "description": "Corner kick awarded", "player": "Bird #5"},
     {"type": "shot", "timestamp": 240, "description": "Header from corner", "player": "Bear #9"},
     {"type": "goal", "timestamp": 242, "description": "Goal from header", "player": "Bear #9"},
     {"type": "substitution", "timestamp": 300, "description": "Tactical change", "player": "Fox #11 for Squirrel #7"},
     {"type": "shot", "timestamp": 360, "description": "Counter attack shot", "player": "Fox #11"},
     {"type": "foul", "timestamp": 420, "description": "Midfield foul", "player": "Rabbit #2"},
     {"type": "shot", "timestamp": 480, "description": "Final shot", "player": "Bunny #1"},
     {"type": "goal", "timestamp": 485, "description": "Winning goal", "player": "Bunny #1"}
   ]'::jsonb);

-- Add demo user to Arsenal team for testing
INSERT INTO team_members (team_id, user_id) VALUES
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '99999999-9999-9999-9999-999999999999');

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