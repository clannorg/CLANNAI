-- Remove all the BS demo teams and games, keep only newmills

-- Step 1: Remove games from fake demo teams
DELETE FROM games WHERE team_id IN (
  SELECT id FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304')
);

-- Step 2: Remove team memberships from fake demo teams  
DELETE FROM team_members WHERE team_id IN (
  SELECT id FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304')
);

-- Step 3: Remove the fake demo teams
DELETE FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304');

-- Step 4: Remove the fake demo users
DELETE FROM users WHERE email IN (
  'arsenal@demo.com', 
  'chelsea@demo.com', 
  'liverpool@demo.com', 
  'city@demo.com', 
  'united@demo.com'
);

-- Step 5: Verify what's left (should only be newmills + company accounts)
SELECT 'TEAMS LEFT:' as type, name, team_code FROM teams
UNION ALL
SELECT 'USERS LEFT:' as type, name, email FROM users
ORDER BY type, name;
