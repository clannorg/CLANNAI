const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { Pool } = require('pg');

// Load environment variables
dotenv.config();

// Create Express app
const app = express();

const PORT = process.env.PORT || 3002;

// Database connection
const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: isAWSRDS || process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Test database connection
pool.on('connect', () => {
  console.log('🗄️ Connected to PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('❌ Database connection error:', err);
});

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true
}));

app.use(express.json({ limit: '5gb' }));
app.use(express.urlencoded({ extended: true, limit: '5gb' }));

// Request logging middleware
app.use((req, res, next) => {
  if (process.env.DEBUG === 'true') {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  }
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    database: 'connected'
  });
});

// API routes placeholder
app.get('/api', (req, res) => {
  res.json({ 
    message: 'ClannAI Backend API',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth/*',
      games: '/api/games/*',
      teams: '/api/teams/*',
      company: '/api/company/*',
      aiChat: '/api/ai-chat/*',
      clips: '/api/clips/*',
      database: '/api/database/*'
    }
  });
});

// Import route modules
const authRoutes = require('./routes/auth');
const gamesRoutes = require('./routes/games');
const teamsRoutes = require('./routes/teams');
const companyRoutes = require('./routes/company');
const aiChatRoutes = require('./routes/ai-chat');
const clipsRoutes = require('./routes/clips');
const databaseRoutes = require('./routes/database');

// Register routes
app.use('/api/auth', authRoutes);
app.use('/api/games', gamesRoutes);
app.use('/api/teams', teamsRoutes);
app.use('/api/company', companyRoutes);
app.use('/api/ai-chat', aiChatRoutes);
app.use('/api/clips', clipsRoutes);
app.use('/api/database', databaseRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ Error:', err);
  
  if (err.name === 'ValidationError') {
    return res.status(400).json({ error: 'Validation error', details: err.message });
  }
  
  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 ClannAI Backend running on port ${PORT}`);
  console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📋 Health check: http://localhost:${PORT}/health`);
  console.log(`🔌 API docs: http://localhost:${PORT}/api`);
});

// Export for testing
module.exports = app; 