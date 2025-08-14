-- Add metadata_url column to games table
-- This stores the URL of the uploaded metadata JSON file for display in company dashboard
-- Migration: add_metadata_url_column.sql
-- Date: 2025-08-14

-- Add the metadata_url column
ALTER TABLE games 
ADD COLUMN metadata_url VARCHAR(500);

-- Add comment for documentation
COMMENT ON COLUMN games.metadata_url IS 'URL of the uploaded metadata JSON file containing team colors, match stats, etc.';

-- Create index for performance (optional, but good practice)
CREATE INDEX IF NOT EXISTS idx_games_metadata_url ON games(metadata_url);

-- Update existing games with metadata_url if needed (optional)
-- This would be run manually if there are existing games that need the URL populated
-- UPDATE games SET metadata_url = 'https://...' WHERE id = '...';