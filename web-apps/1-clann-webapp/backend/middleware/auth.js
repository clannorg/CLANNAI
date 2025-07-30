const jwt = require('jsonwebtoken');
const { Pool } = require('pg');

const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: isAWSRDS || process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Verify JWT token and get user
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Get user from database
    const userResult = await pool.query(
      'SELECT id, email, name, role, is_active FROM users WHERE id = $1',
      [decoded.userId]
    );

    if (userResult.rows.length === 0) {
      return res.status(401).json({ error: 'User not found' });
    }

    const user = userResult.rows[0];

    if (!user.is_active) {
      return res.status(401).json({ error: 'Account deactivated' });
    }

    // Add user to request object
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(403).json({ error: 'Invalid token' });
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(403).json({ error: 'Token expired' });
    }
    
    console.error('Auth middleware error:', error);
    return res.status(500).json({ error: 'Authentication error' });
  }
};

// Check if user has company role
const requireCompanyRole = (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  if (req.user.role !== 'company') {
    return res.status(403).json({ error: 'Company access required' });
  }

  next();
};

// Check if user owns resource or has company role
const requireOwnershipOrCompany = (userIdField = 'uploaded_by') => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Company users can access everything
    if (req.user.role === 'company') {
      return next();
    }

    // Regular users can only access their own resources
    // This will be checked in the route handler with the specific resource
    req.requireOwnership = true;
    req.ownershipField = userIdField;
    next();
  };
};

module.exports = {
  authenticateToken,
  requireCompanyRole,
  requireOwnershipOrCompany
}; 