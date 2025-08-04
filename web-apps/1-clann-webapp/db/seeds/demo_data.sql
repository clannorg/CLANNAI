-- ClannAI Platform - Essential Accounts Only
-- Company accounts for admin/analysis functionality

-- Insert essential company users only
INSERT INTO users (id, email, password_hash, name, role) VALUES
  ('99999999-9999-9999-9999-999999999999', 'demo@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'Demo User', 'user'),
  ('88888888-8888-8888-8888-888888888888', 'admin@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'ClannAI Admin', 'company'),
  ('77777777-7777-7777-7777-777777777777', 'analyst@clann.ai', '$2b$10$sW7qjE7P4.6BjXI0vJ9X2eCr8jE9VjK4bR2L8wX3sA1mN6pQ5tY7z', 'ClannAI Analyst', 'company');

-- Note: 
-- - Newmills team (TQJ1Q5) exists separately with real footage
-- - No fake demo teams needed - users get demo content via newmills "ops2" game
-- - Clean, simple setup focused on real usage