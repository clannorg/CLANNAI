-- Migration: Add is_demo column to games table
-- This allows marking games as demo content visible to all users

ALTER TABLE games 
ADD COLUMN is_demo BOOLEAN DEFAULT false;

-- Add index for performance
CREATE INDEX idx_games_is_demo ON games(is_demo);

-- Add comment for documentation
COMMENT ON COLUMN games.is_demo IS 'Demo games visible to all users regardless of team membership';

-- Mark existing demo games as demo content
UPDATE games 
SET is_demo = true 
WHERE id IN (
  '11111111-1269-0511-0000-000000000000', -- Arsenal vs Local Academy
  '22222222-2277-0526-0000-000000000000', -- Chelsea vs Brighton Academy
  '33333333-3297-0616-0000-000000000000', -- Liverpool vs Everton U21
  '44444444-4298-0601-0000-000000000000', -- City vs Newcastle Academy
  '55555555-5304-0618-0000-000000000000', -- United vs Tottenham U21
  '99999999-9999-9999-9999-999999999999'  -- Demo Video Test
);

-- Verify the update
SELECT title, is_demo, status FROM games WHERE is_demo = true ORDER BY title;