-- Migration: Add HLS conversions table
-- This table tracks MediaConvert jobs for HLS streaming

CREATE TABLE IF NOT EXISTS hls_conversions (
    id SERIAL PRIMARY KEY,
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    job_id VARCHAR(255) NOT NULL, -- MediaConvert job ID
    status VARCHAR(50) NOT NULL DEFAULT 'IN_PROGRESS', -- IN_PROGRESS, COMPLETE, ERROR
    progress INTEGER DEFAULT 0, -- 0-100 percentage
    hls_url TEXT, -- S3 URL to the master playlist (.m3u8)
    output_path TEXT NOT NULL, -- S3 path where HLS files are stored
    error_message TEXT, -- Error details if conversion fails
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_hls_conversions_game_id ON hls_conversions(game_id);
CREATE INDEX IF NOT EXISTS idx_hls_conversions_status ON hls_conversions(status);
CREATE INDEX IF NOT EXISTS idx_hls_conversions_job_id ON hls_conversions(job_id);

-- Add HLS URL column to games table (optional - for quick access)
ALTER TABLE games ADD COLUMN IF NOT EXISTS hls_url TEXT;
ALTER TABLE games ADD COLUMN IF NOT EXISTS hls_status VARCHAR(50) DEFAULT 'NOT_CONVERTED'; -- NOT_CONVERTED, CONVERTING, AVAILABLE

-- Update trigger to sync HLS status with games table
CREATE OR REPLACE FUNCTION update_game_hls_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the games table with latest HLS status
    UPDATE games 
    SET 
        hls_url = CASE WHEN NEW.status = 'COMPLETE' THEN NEW.hls_url ELSE NULL END,
        hls_status = CASE 
            WHEN NEW.status = 'COMPLETE' THEN 'AVAILABLE'
            WHEN NEW.status = 'IN_PROGRESS' THEN 'CONVERTING'
            ELSE 'NOT_CONVERTED'
        END
    WHERE id = NEW.game_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_game_hls_status ON hls_conversions;
CREATE TRIGGER trigger_update_game_hls_status
    AFTER INSERT OR UPDATE ON hls_conversions
    FOR EACH ROW
    EXECUTE FUNCTION update_game_hls_status();