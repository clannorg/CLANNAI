-- Migration: Add analysis video URLs to games table
-- Similar to web-app-clannai structure with analysis_video1_url through analysis_video5_url

ALTER TABLE games 
ADD COLUMN analysis_video1_url VARCHAR(500),
ADD COLUMN analysis_video2_url VARCHAR(500),
ADD COLUMN analysis_video3_url VARCHAR(500),
ADD COLUMN analysis_video4_url VARCHAR(500),
ADD COLUMN analysis_video5_url VARCHAR(500);

-- Update status enum to include 'analyzed' state
-- (status column already exists with 'pending' default)

-- Create index for faster queries on analyzed games
CREATE INDEX idx_games_analysis_status ON games(status) WHERE status = 'analyzed';

-- Add comment for documentation
COMMENT ON COLUMN games.analysis_video1_url IS 'S3 URL for first analysis video highlight';
COMMENT ON COLUMN games.analysis_video2_url IS 'S3 URL for second analysis video highlight';  
COMMENT ON COLUMN games.analysis_video3_url IS 'S3 URL for third analysis video highlight';
COMMENT ON COLUMN games.analysis_video4_url IS 'S3 URL for fourth analysis video highlight';
COMMENT ON COLUMN games.analysis_video5_url IS 'S3 URL for fifth analysis video highlight'; 