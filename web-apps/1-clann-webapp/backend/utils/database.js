const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || `postgresql://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_NAME}`,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Get user by email
const getUserByEmail = async (email) => {
  const result = await pool.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0];
};

// Get user by ID
const getUserById = async (id) => {
  const result = await pool.query(
    'SELECT id, email, name, role, avatar_url, is_active, created_at FROM users WHERE id = $1',
    [id]
  );
  return result.rows[0];
};

// Create new user
const createUser = async (email, passwordHash, phone, role = 'user') => {
  const result = await pool.query(
    `INSERT INTO users (email, password_hash, name, role) 
     VALUES ($1, $2, $3, $4) 
     RETURNING id, email, name, role, created_at`,
    [email, passwordHash, phone, role]
  );
  return result.rows[0];
};

// Get team by ID
const getTeamById = async (id) => {
  const result = await pool.query(
    'SELECT * FROM teams WHERE id = $1',
    [id]
  );
  return result.rows[0];
};

// Get team by join code
const getTeamByCode = async (code) => {
  const result = await pool.query(
    'SELECT * FROM teams WHERE team_code = $1',
    [code]
  );
  return result.rows[0];
};

// Check if user is team member
const isTeamMember = async (userId, teamId) => {
  const result = await pool.query(
    'SELECT 1 FROM team_members WHERE user_id = $1 AND team_id = $2',
    [userId, teamId]
  );
  return result.rows.length > 0;
};

// Add user to team
const addUserToTeam = async (userId, teamId) => {
  const result = await pool.query(
    `INSERT INTO team_members (user_id, team_id) 
     VALUES ($1, $2) 
     ON CONFLICT (user_id, team_id) DO NOTHING
     RETURNING *`,
    [userId, teamId]
  );
  return result.rows[0];
};

// Get user's teams
const getUserTeams = async (userId) => {
  const result = await pool.query(
    `SELECT t.id, t.name, t.description, t.color, t.team_code, t.logo_url, t.is_public,
            t.created_at, tm.joined_at,
            (t.owner_id = $1) as is_owner
     FROM teams t
     JOIN team_members tm ON t.id = tm.team_id
     WHERE tm.user_id = $1
     ORDER BY tm.joined_at DESC`,
    [userId]
  );
  return result.rows;
};

// Get games for user (based on their teams)
const getUserGames = async (userId) => {
  const result = await pool.query(
    `SELECT g.*, t.name as team_name, t.color as team_color
     FROM games g
     JOIN teams t ON g.team_id = t.id
     JOIN team_members tm ON t.id = tm.team_id
     WHERE tm.user_id = $1
     ORDER BY g.created_at DESC`,
    [userId]
  );
  return result.rows;
};

// Get all games (company view)
const getAllGames = async () => {
  const result = await pool.query(
    `SELECT g.*, t.name as team_name, t.color as team_color,
            u.name as uploaded_by_name, u.email as uploaded_by_email
     FROM games g
     JOIN teams t ON g.team_id = t.id
     JOIN users u ON g.uploaded_by = u.id
     ORDER BY g.created_at DESC`
  );
  return result.rows;
};

// Get game by ID
const getGameById = async (id) => {
  const result = await pool.query(
    `SELECT g.*, t.name as team_name, t.color as team_color,
            u.name as uploaded_by_name, u.email as uploaded_by_email
     FROM games g
     JOIN teams t ON g.team_id = t.id
     JOIN users u ON g.uploaded_by = u.id
     WHERE g.id = $1`,
    [id]
  );
  return result.rows[0];
};

// Create new game
const createGame = async (title, description, videoUrl, teamId, uploadedBy, fileType = 'veo') => {
  const result = await pool.query(
    `INSERT INTO games (title, description, video_url, team_id, uploaded_by, file_type, status)
     VALUES ($1, $2, $3, $4, $5, $6, 'pending')
     RETURNING *`,
    [title, description, videoUrl, teamId, uploadedBy, fileType]
  );
  return result.rows[0];
};

// Update game
const updateGame = async (id, updates) => {
  const fields = [];
  const values = [];
  let paramCount = 1;

  Object.keys(updates).forEach(key => {
    if (updates[key] !== undefined) {
      fields.push(`${key} = $${paramCount}`);
      values.push(updates[key]);
      paramCount++;
    }
  });

  if (fields.length === 0) {
    throw new Error('No fields to update');
  }

  fields.push('updated_at = NOW()');
  values.push(id);

  const query = `
    UPDATE games 
    SET ${fields.join(', ')}
    WHERE id = $${paramCount}
    RETURNING *
  `;

  const result = await pool.query(query, values);
  return result.rows[0];
};

// Create new team with auto-generated team code
const createTeam = async (name, description, ownerId, color = '#016F32') => {
  // Generate unique team code
  const generateTeamCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  };

  let teamCode;
  let attempts = 0;
  const maxAttempts = 10;

  // Keep generating codes until we find a unique one
  while (attempts < maxAttempts) {
    teamCode = generateTeamCode();
    const existing = await pool.query('SELECT id FROM teams WHERE team_code = $1', [teamCode]);
    if (existing.rows.length === 0) {
      break;
    }
    attempts++;
  }

  if (attempts >= maxAttempts) {
    throw new Error('Failed to generate unique team code');
  }

  const result = await pool.query(
    `INSERT INTO teams (name, description, color, team_code, owner_id) 
     VALUES ($1, $2, $3, $4, $5) 
     RETURNING *`,
    [name, description || null, color, teamCode, ownerId]
  );

  const team = result.rows[0];

  // Automatically add the owner as a team member
  await addUserToTeam(ownerId, team.id);

  return team;
};

module.exports = {
  pool,
  getUserByEmail,
  getUserById,
  createUser,
  getTeamById,
  getTeamByCode,
  createTeam,
  isTeamMember,
  addUserToTeam,
  getUserTeams,
  getUserGames,
  getAllGames,
  getGameById,
  createGame,
  updateGame
}; 