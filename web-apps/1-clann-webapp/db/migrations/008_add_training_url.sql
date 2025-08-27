-- Add training_url column to games table for training recommendations
-- This replaces the chunks_base_url functionality with training recommendations

-- Add the training_url column
ALTER TABLE games 
ADD COLUMN IF NOT EXISTS training_url TEXT;

-- Add comment for documentation
COMMENT ON COLUMN games.training_url IS 'URL for training recommendations JSON file (e.g., https://bucket.s3.amazonaws.com/analysis-data/game-id-training.json)';

-- Optional: Remove chunks_base_url if no longer needed
-- ALTER TABLE games DROP COLUMN IF EXISTS chunks_base_url;
