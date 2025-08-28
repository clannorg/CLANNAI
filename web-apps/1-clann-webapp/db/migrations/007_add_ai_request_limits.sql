-- Add AI request tracking for rate limiting
-- This tracks daily AI requests per user to enforce limits for non-company users

CREATE TABLE IF NOT EXISTS ai_request_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_date DATE NOT NULL DEFAULT CURRENT_DATE,
    request_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one record per user per day
    UNIQUE(user_id, request_date)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_ai_request_usage_user_date ON ai_request_usage(user_id, request_date);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_ai_request_usage_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_ai_request_usage_updated_at
    BEFORE UPDATE ON ai_request_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_request_usage_updated_at();
