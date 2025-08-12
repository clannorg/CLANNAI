DELETE FROM games WHERE team_id IN (SELECT id FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304'));
DELETE FROM team_members WHERE team_id IN (SELECT id FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304'));
DELETE FROM teams WHERE team_code IN ('ARS269', 'CHE277', 'LIV297', 'MCI298', 'MUN304');
DELETE FROM users WHERE email IN ('arsenal@demo.com', 'chelsea@demo.com', 'liverpool@demo.com', 'city@demo.com', 'united@demo.com');