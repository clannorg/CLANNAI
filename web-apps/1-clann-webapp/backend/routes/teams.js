const express = require('express');
const { Pool } = require('pg');
const { authenticateToken } = require('../middleware/auth');
const { 
  getTeamByCode, 
  addUserToTeam, 
  removeUserFromTeam,
  getUserTeams, 
  getTeamById,
  createTeam,
  isTeamMember 
} = require('../utils/database');

// Initialize database pool
const isAWSRDS = process.env.DATABASE_URL && process.env.DATABASE_URL.includes('rds.amazonaws.com');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: isAWSRDS ? { 
    rejectUnauthorized: false,
    require: true 
  } : false
});

const router = express.Router();

// Create new team
router.post('/create', authenticateToken, async (req, res) => {
  try {
    const { name, description, color } = req.body;

    if (!name || name.trim().length === 0) {
      return res.status(400).json({ error: 'Team name is required' });
    }

    if (name.trim().length > 255) {
      return res.status(400).json({ error: 'Team name is too long (max 255 characters)' });
    }

    // Create the team
    const team = await createTeam(
      name.trim(), 
      description?.trim() || null, 
      req.user.id, 
      color || '#016F32'
    );

    res.status(201).json({
      message: 'Team created successfully',
      team: {
        id: team.id,
        name: team.name,
        description: team.description,
        color: team.color,
        team_code: team.team_code,
        logo_url: team.logo_url,
        is_public: team.is_public,
        is_owner: true,
        created_at: team.created_at
      }
    });
  } catch (error) {
    console.error('Create team error:', error);
    res.status(500).json({ error: 'Failed to create team' });
  }
});

// Join team by code
// Join team by invite code
router.post('/join-by-code', authenticateToken, async (req, res) => {
  try {
    const { inviteCode } = req.body;

    if (!inviteCode) {
      return res.status(400).json({ error: 'Invite code is required' });
    }

    // Find team by invite code
    const teamResult = await pool.query(
      'SELECT id, name, team_code FROM teams WHERE team_code = $1',
      [inviteCode]
    );

    if (teamResult.rows.length === 0) {
      return res.status(404).json({ error: 'Invalid invite code' });
    }

    const team = teamResult.rows[0];

    // Check if user is already a member
    const memberResult = await pool.query(
      'SELECT id FROM team_members WHERE team_id = $1 AND user_id = $2',
      [team.id, req.user.id]
    );

    if (memberResult.rows.length > 0) {
      return res.status(400).json({ error: 'You are already a member of this team' });
    }

    // Add user to team
    await pool.query(
      'INSERT INTO team_members (team_id, user_id) VALUES ($1, $2)',
      [team.id, req.user.id]
    );

    res.json({
      message: 'Successfully joined team',
      team: {
        id: team.id,
        name: team.name,
        team_code: team.team_code
      }
    });
  } catch (error) {
    console.error('Join team by code error:', error);
    res.status(500).json({ error: 'Failed to join team' });
  }
});

router.post('/join', authenticateToken, async (req, res) => {
  try {
    const { teamCode } = req.body;

    if (!teamCode) {
      return res.status(400).json({ error: 'Team code is required' });
    }

    // Find team by code
    const team = await getTeamByCode(teamCode.toUpperCase());
    if (!team) {
      return res.status(404).json({ error: 'Invalid team code' });
    }

    // Check if user is already a member
    const alreadyMember = await isTeamMember(req.user.id, team.id);
    if (alreadyMember) {
      return res.status(409).json({ 
        error: 'You are already a member of this team',
        team: {
          id: team.id,
          name: team.name,
          code: team.team_code
        }
      });
    }

    // Add user to team
    await addUserToTeam(req.user.id, team.id);

    res.json({
      message: 'Successfully joined team',
      team: {
        id: team.id,
        name: team.name,
        description: team.description,
        color: team.color,
        team_code: team.team_code,
        logo_url: team.logo_url,
        is_public: team.is_public
      }
    });
  } catch (error) {
    console.error('Join team error:', error);
    res.status(500).json({ error: 'Failed to join team' });
  }
});

// Get user's teams
router.get('/my-teams', authenticateToken, async (req, res) => {
  try {
    const teams = await getUserTeams(req.user.id);

    res.json({
      teams: teams.map(team => ({
        id: team.id,
        name: team.name,
        description: team.description,
        color: team.color,
        team_code: team.team_code,
        logo_url: team.logo_url,
        is_public: team.is_public,
        is_owner: team.is_owner,
        joined_at: team.joined_at,
        created_at: team.created_at
      }))
    });
  } catch (error) {
    console.error('Get teams error:', error);
    res.status(500).json({ error: 'Failed to get teams' });
  }
});

// Get team by ID
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const teamId = req.params.id;

    // Check if user is a member of this team
    const isMember = await isTeamMember(req.user.id, teamId);
    if (!isMember && req.user.role !== 'company') {
      return res.status(403).json({ error: 'You are not a member of this team' });
    }

    const team = await getTeamById(teamId);
    if (!team) {
      return res.status(404).json({ error: 'Team not found' });
    }

    res.json({
      team: {
        id: team.id,
        name: team.name,
        description: team.description,
        color: team.color,
        team_code: team.team_code,
        logo_url: team.logo_url,
        is_public: team.is_public,
        created_at: team.created_at,
        owner_id: team.owner_id
      }
    });
  } catch (error) {
    console.error('Get team error:', error);
    res.status(500).json({ error: 'Failed to get team' });
  }
});

// Get team join codes (for demo purposes)
router.get('/codes/demo', (req, res) => {
  res.json({
    message: 'Demo team join codes',
    codes: [
      { code: 'ARS269', team: 'Arsenal FC Academy' },
      { code: 'CHE277', team: 'Chelsea Youth' },
      { code: 'LIV297', team: 'Liverpool Reserves' },
      { code: 'MCI298', team: 'City Development' },
      { code: 'MUN304', team: 'United U21s' }
    ]
  });
});

// Leave team
router.post('/:id/leave', authenticateToken, async (req, res) => {
  try {
    const teamId = req.params.id; // Keep as UUID string, don't parse as integer
    const userId = req.user.id;

    if (!teamId) {
      return res.status(400).json({ error: 'Invalid team ID' });
    }

    // Check if user is a member of the team
    const isMember = await isTeamMember(userId, teamId);
    if (!isMember) {
      return res.status(400).json({ error: 'You are not a member of this team' });
    }

    // Remove user from team
    const result = await removeUserFromTeam(userId, teamId);

    res.json({
      message: 'Successfully left team',
      success: true
    });

  } catch (error) {
    console.error('Error leaving team:', error);
    res.status(500).json({ 
      error: error.message || 'Failed to leave team' 
    });
  }
});

module.exports = router; 