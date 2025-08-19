-- Migration: Add events_modified column for manual annotation tool
-- This stores user-edited events (binned, time-adjusted, etc.)

ALTER TABLE games 
ADD COLUMN events_modified JSONB,
ADD COLUMN events_last_modified_by UUID REFERENCES users(id),
ADD COLUMN events_last_modified_at TIMESTAMP;

-- Add index for performance on events_modified queries
CREATE INDEX idx_games_events_modified ON games USING GIN (events_modified);
CREATE INDEX idx_games_events_last_modified_by ON games(events_last_modified_by);

-- Add comment explaining the column
COMMENT ON COLUMN games.events_modified IS 'User-edited events JSON - overrides ai_analysis events when present';
COMMENT ON COLUMN games.events_last_modified_by IS 'User who last modified the events';
COMMENT ON COLUMN games.events_last_modified_at IS 'Timestamp of last events modification';