const { Pool } = require('pg');

const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: isAWSRDS || process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Rate limiting configuration
const AI_REQUEST_LIMITS = {
  company: -1,    // Unlimited for company users (-1 means no limit)
  regular: 5      // 5 requests per day for regular users
};

/**
 * Rate limiter middleware for AI chat requests
 * Limits non-company users to 5 requests per day
 */
const aiChatRateLimit = async (req, res, next) => {
  try {
    // Company users have unlimited access
    if (req.user.role === 'company') {
      return next();
    }

    const userId = req.user.id;
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

    // Get or create today's usage record
    const upsertQuery = `
      INSERT INTO ai_request_usage (user_id, request_date, request_count)
      VALUES ($1, $2, 1)
      ON CONFLICT (user_id, request_date)
      DO UPDATE SET 
        request_count = ai_request_usage.request_count + 1,
        updated_at = CURRENT_TIMESTAMP
      RETURNING request_count;
    `;

    const result = await pool.query(upsertQuery, [userId, today]);
    const currentCount = result.rows[0].request_count;

    // Check if user has exceeded their limit
    const userLimit = AI_REQUEST_LIMITS.regular;
    if (currentCount > userLimit) {
      return res.status(429).json({
        error: 'Daily AI request limit exceeded',
        message: `You have reached your daily limit of ${userLimit} AI coaching requests. Limit resets at midnight.`,
        limit: userLimit,
        current: currentCount,
        resetTime: 'midnight UTC'
      });
    }

    // Add usage info to request for logging
    req.aiUsage = {
      current: currentCount,
      limit: userLimit,
      remaining: userLimit - currentCount
    };

    next();
  } catch (error) {
    console.error('Rate limiter error:', error);
    
    // On database error, allow the request but log the issue
    // This prevents rate limiting from breaking the app if DB is down
    console.warn('Rate limiting failed, allowing request through');
    next();
  }
};

/**
 * Get current AI usage for a user
 */
const getAiUsage = async (userId) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    
    const result = await pool.query(
      'SELECT request_count FROM ai_request_usage WHERE user_id = $1 AND request_date = $2',
      [userId, today]
    );

    const currentCount = result.rows.length > 0 ? result.rows[0].request_count : 0;
    
    return {
      current: currentCount,
      limit: AI_REQUEST_LIMITS.regular,
      remaining: Math.max(0, AI_REQUEST_LIMITS.regular - currentCount),
      resetTime: 'midnight UTC'
    };
  } catch (error) {
    console.error('Error getting AI usage:', error);
    return {
      current: 0,
      limit: AI_REQUEST_LIMITS.regular,
      remaining: AI_REQUEST_LIMITS.regular,
      resetTime: 'midnight UTC'
    };
  }
};

module.exports = {
  aiChatRateLimit,
  getAiUsage,
  AI_REQUEST_LIMITS
};
