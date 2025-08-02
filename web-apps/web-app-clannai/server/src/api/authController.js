const bcrypt = require("bcryptjs");
const jwt = require('jsonwebtoken');
const db = require("../db");

const DEMO_TEAM_ID = '63bf8bce-72c4-4533-b090-e4c0be7c593e';

const generateToken = (user) => {
    return jwt.sign(
        { id: user.id, email: user.email, role: user.role },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );
};

exports.login = async (req, res) => {
    const { email, password } = req.body;

    try {
        const result = await db.query("SELECT * FROM Users WHERE email = $1", [email]);
        const user = result.rows[0];
        
        if (user && await bcrypt.compare(password, user.password_hash)) {
            // Get user's primary team (most recent team they joined)
            const teamResult = await db.query(
                `SELECT team_id FROM TeamMembers WHERE user_id = $1 ORDER BY joined_at DESC LIMIT 1`,
                [user.id]
            );
            const teamId = teamResult.rows[0]?.team_id || null;
            
            const token = jwt.sign(
                { id: user.id, email: user.email, role: user.role, teamId },
                process.env.JWT_SECRET,
                { expiresIn: '24h' }
            );
            
            res.json({
                token,
                id: user.id,
                email: user.email,
                role: user.role,
                teamId
            });
        } else {
            res.status(401).json({ error: "Invalid credentials" });
        }
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.register = async (req, res) => {
    try {
        const { email, password, termsAccepted } = req.body;
        
        if (!termsAccepted) {
            return res.status(400).json({ error: 'Terms & Conditions must be accepted' });
        }

        await db.query('BEGIN');

        try {
            const hashedPassword = await bcrypt.hash(password, 10);
            const newUser = await db.query(
                'INSERT INTO Users (email, password_hash, role) VALUES ($1, $2, $3) RETURNING *',
                [email, hashedPassword, 'USER']
            );

            const teamMember = await db.query(
                'INSERT INTO TeamMembers (user_id, team_id, is_admin) VALUES ($1, $2, $3) RETURNING *',
                [newUser.rows[0].id, DEMO_TEAM_ID, false]
            );

            await db.query('COMMIT');

            const token = jwt.sign(
                {
                    id: newUser.rows[0].id,
                    email: newUser.rows[0].email,
                    role: newUser.rows[0].role,
                    teamId: DEMO_TEAM_ID
                },
                process.env.JWT_SECRET,
                { expiresIn: '24h' }
            );

            res.status(201).json({
                token,
                id: newUser.rows[0].id,
                email: newUser.rows[0].email,
                role: newUser.rows[0].role,
                teamId: DEMO_TEAM_ID
            });

        } catch (error) {
            await db.query('ROLLBACK');
            throw error;
        }

    } catch (error) {
        res.status(500).json({
            error: 'Registration failed',
            details: error.message
        });
    }
};

exports.deleteAccount = async (req, res) => {
    const userId = req.user.id;
    try {
        await db.query('BEGIN');
        await db.query("DELETE FROM Sessions WHERE uploaded_by = $1", [userId]);
        await db.query("DELETE FROM TeamMembers WHERE user_id = $1", [userId]);
        await db.query("DELETE FROM Users WHERE id = $1", [userId]);
        await db.query('COMMIT');
        res.json({ message: "Account deleted successfully" });
    } catch (err) {
        await db.query('ROLLBACK');
        res.status(500).json({ error: 'Failed to delete account' });
    }
};

module.exports = {
    register: exports.register,
    deleteAccount: exports.deleteAccount,
    login: exports.login
};
