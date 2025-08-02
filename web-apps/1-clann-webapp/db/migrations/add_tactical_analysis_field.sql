-- Add tactical_analysis field to games table
-- This will store tactical insights directly in the database like ai_analysis does for events

ALTER TABLE games 
ADD COLUMN tactical_analysis JSONB;

-- Add index for performance
CREATE INDEX idx_games_tactical_analysis ON games USING GIN(tactical_analysis);

-- Comments for clarity
COMMENT ON COLUMN games.tactical_analysis IS 'Store tactical analysis data directly (match summary, team analysis, training priorities, etc.)';
COMMENT ON COLUMN games.ai_analysis IS 'Store game events and AI analysis data';
COMMENT ON COLUMN games.metadata IS 'Store file references and other metadata';