-- Add chunks_base_url column to games table for pre-chunked video clips
-- This allows company users to specify a base URL for pre-made video chunks
-- enabling fast clip creation without MediaConvert processing

ALTER TABLE games 
ADD COLUMN chunks_base_url TEXT;

-- Add comment to document the column purpose
COMMENT ON COLUMN games.chunks_base_url IS 'Base URL for pre-chunked video segments (e.g., https://bucket.s3.amazonaws.com/clips/game-id/)';