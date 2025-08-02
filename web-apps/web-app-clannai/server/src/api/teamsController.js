const db = require("../db");
const { MAX_TEAM_MEMBERS } = require('../constants');

// Helper function to add a company member to all existing teams
exports.addCompanyMemberToAllTeams = async (companyMemberId) => {
    try {
        // Get all teams
        const teams = await db.query('SELECT id FROM Teams');
        
        // Add the company member to each team (if not already a member)
        for (const team of teams.rows) {
            await db.query(
                `INSERT INTO TeamMembers (team_id, user_id, is_admin) 
                 VALUES ($1, $2, $3) 
                 ON CONFLICT (team_id, user_id) DO NOTHING`,
                [team.id, companyMemberId, false]
            );
        }
        
        return true;
    } catch (err) {
        console.error('Error adding company member to all teams:', err);
        return false;
    }
};

exports.getUserTeams = async (req, res) => {
    const userId = req.user.id;

    try {
        const result = await db.query(`
            SELECT t.*, tm.is_admin 
            FROM Teams t
            INNER JOIN TeamMembers tm ON t.id = tm.team_id
            WHERE tm.user_id = $1
            ORDER BY t.created_at DESC
        `, [userId]);

        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch teams' });
    }
};

exports.createTeam = async (req, res) => {
    const { name, team_code } = req.body;
    const userId = req.user.id;

    try {
        await db.query('BEGIN');

        const teamResult = await db.query(`
            INSERT INTO Teams (name, team_code)
            VALUES ($1, $2)
            RETURNING id, name, team_code
        `, [name, team_code]);

        await db.query(`
            INSERT INTO TeamMembers (team_id, user_id, is_admin)
            VALUES ($1, $2, true)
        `, [teamResult.rows[0].id, userId]);

        // Auto-add all company members to new teams (hidden from regular users)
        const companyMembers = await db.query(
            'SELECT id FROM Users WHERE role = $1 AND id != $2',
            ['COMPANY_MEMBER', userId]
        );
        
        for (const companyMember of companyMembers.rows) {
            await db.query(
                "INSERT INTO TeamMembers (team_id, user_id, is_admin) VALUES ($1, $2, $3)",
                [teamResult.rows[0].id, companyMember.id, false]
            );
        }

        await db.query('COMMIT');

        res.json(teamResult.rows[0]);
    } catch (err) {
        await db.query('ROLLBACK');
        res.status(500).json({ error: 'Failed to create team' });
    }
};

exports.joinTeam = async (req, res) => {
    const { team_code } = req.body;
    const userId = req.user.id;

    try {
        // First find the team
        const teamResult = await db.query(
            `SELECT id, team_code, name 
             FROM Teams 
             WHERE team_code = $1`,
            [team_code]
        );

        if (teamResult.rows.length === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }

        const teamId = teamResult.rows[0].id;
        const teamName = teamResult.rows[0].name;
        const isStMarys = teamResult.rows[0].team_code === 'STMARY';

        // For St Mary's team, only the original admin should be admin
        const isAdmin = false;  // Default to false for all joins

        // Add user to team
        await db.query(
            `INSERT INTO TeamMembers (team_id, user_id, is_admin)
             VALUES ($1, $2, $3)`,
            [teamId, userId, isAdmin]
        );

        res.json({
            message: 'Successfully joined team',
            team_id: teamId,
            team_name: teamName
        });
    } catch (err) {
        console.error('Join team error:', err);
        // If the error is a duplicate key violation, the user is already in the team
        if (err.code === '23505') { // Unique violation error code
            return res.json({
                message: 'Already a member of this team',
                team_id: teamId,
                team_name: teamName
            });
        }
        res.status(500).json({ error: 'Failed to join team' });
    }
};

exports.getTeamMembers = async (req, res) => {
    const { teamId } = req.params;
    const userId = req.user.id;

    try {
        // First check if this is St Mary's team
        const teamCheck = await db.query(
            `SELECT t.team_code, t.name, tm.is_admin
             FROM Teams t
             LEFT JOIN TeamMembers tm ON tm.team_id = t.id AND tm.user_id = $1
             WHERE t.id = $2`,
            [userId, teamId]
        );

        // If it's St Mary's team, only allow company members to view
        if (teamCheck.rows[0]?.team_code === 'STMARY') {
            const userRole = await db.query(
                'SELECT role FROM Users WHERE id = $1',
                [userId]
            );

            if (userRole.rows[0]?.role !== 'COMPANY_MEMBER') {
                return res.status(403).json({
                    error: 'Demo team members are private'
                });
            }
        }

        // For non-St Mary's teams, only show members to team admins
        if (!teamCheck.rows[0]?.is_admin && teamCheck.rows[0]?.team_code !== 'STMARY') {
            return res.status(403).json({
                error: 'Only team admins can view member list'
            });
        }

        // Get current user's role to determine what members to show
        const currentUserRole = await db.query(
            'SELECT role FROM Users WHERE id = $1',
            [userId]
        );
        
        // Get team members - hide company members from regular users
        let membersQuery;
        let queryParams;
        
        if (currentUserRole.rows[0]?.role === 'COMPANY_MEMBER') {
            // Company members can see all members including other company members
            membersQuery = `SELECT 
                u.id,
                u.email,
                u.created_at,
                u.role,
                tm.is_admin
             FROM TeamMembers tm
             JOIN Users u ON u.id = tm.user_id
             WHERE tm.team_id = $1
             ORDER BY tm.is_admin DESC, u.created_at ASC`;
            queryParams = [teamId];
        } else {
            // Regular users only see other regular users (hide company members)
            membersQuery = `SELECT 
                u.id,
                u.email,
                u.created_at,
                u.role,
                tm.is_admin
             FROM TeamMembers tm
             JOIN Users u ON u.id = tm.user_id
             WHERE tm.team_id = $1 AND u.role != 'COMPANY_MEMBER'
             ORDER BY tm.is_admin DESC, u.created_at ASC`;
            queryParams = [teamId];
        }
        
        const members = await db.query(membersQuery, queryParams);

        res.json(members.rows);
    } catch (err) {
        res.status(500).json({ error: 'Failed to get team members' });
    }
};

exports.updateTeamColors = async (req, res) => {
    const { teamId } = req.params;
    const { home_color, away_color } = req.body;
    const userId = req.user.id;

    try {
        // Check if user is admin of this team
        const adminCheck = await db.query(
            `SELECT tm.is_admin 
             FROM TeamMembers tm 
             WHERE tm.team_id = $1 AND tm.user_id = $2`,
            [teamId, userId]
        );

        if (!adminCheck.rows[0]?.is_admin) {
            return res.status(403).json({ 
                error: 'Only team admins can change team colors' 
            });
        }

        // Validate color format (hex colors)
        const hexColorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
        if (home_color && !hexColorRegex.test(home_color)) {
            return res.status(400).json({ error: 'Invalid home color format' });
        }
        if (away_color && !hexColorRegex.test(away_color)) {
            return res.status(400).json({ error: 'Invalid away color format' });
        }

        // Update team colors
        const updateQuery = `
            UPDATE Teams 
            SET 
                home_color = COALESCE($1, home_color),
                away_color = COALESCE($2, away_color)
            WHERE id = $3
            RETURNING id, name, team_code, home_color, away_color
        `;
        
        const result = await db.query(updateQuery, [home_color, away_color, teamId]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }

        res.json(result.rows[0]);
    } catch (err) {
        console.error('Update team colors error:', err);
        res.status(500).json({ error: 'Failed to update team colors' });
    }
};

exports.getTeamColors = async (req, res) => {
    const { teamId } = req.params;
    const userId = req.user.id;

    try {
        // Check if user is member of this team
        const memberCheck = await db.query(
            `SELECT tm.is_admin 
             FROM TeamMembers tm 
             WHERE tm.team_id = $1 AND tm.user_id = $2`,
            [teamId, userId]
        );

        if (memberCheck.rows.length === 0) {
            return res.status(403).json({ 
                error: 'Access denied - not a team member' 
            });
        }

        // Get team colors
        const result = await db.query(
            `SELECT id, name, team_code, home_color, away_color 
             FROM Teams 
             WHERE id = $1`,
            [teamId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }

        res.json({
            ...result.rows[0],
            is_admin: memberCheck.rows[0].is_admin
        });
    } catch (err) {
        console.error('Get team colors error:', err);
        res.status(500).json({ error: 'Failed to get team colors' });
    }
};

exports.removeTeamMember = async (req, res) => {
    const { teamId, userId } = req.params;
    const requestingUserId = req.user.id;

    try {
        // Check if user is a company member
        const userRole = await db.query(
            'SELECT role FROM Users WHERE id = $1',
            [requestingUserId]
        );

        const isCompanyMember = userRole.rows[0]?.role === 'COMPANY_MEMBER';

        if (!isCompanyMember) {
            // If not a company member, check if user is team admin
            const requestingUserCheck = await db.query(
                `SELECT is_admin 
                 FROM TeamMembers 
                 WHERE team_id = $1 AND user_id = $2`,
                [teamId, requestingUserId]
            );

            if (!requestingUserCheck.rows[0]?.is_admin) {
                return res.status(403).json({ error: 'Only team admins or company members can remove team members' });
            }
        }

        // Remove the team member
        await db.query(
            `DELETE FROM TeamMembers 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, userId]
        );

        res.json({ message: 'Team member removed successfully' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to remove team member' });
    }
};

exports.promoteToAdmin = async (req, res) => {
    const { teamId, userId: memberToPromoteId } = req.params;
    const requestingUserId = req.user.id;

    try {
        // Check if requesting user is admin
        const requestingUserCheck = await db.query(
            `SELECT is_admin 
             FROM TeamMembers 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, requestingUserId]
        );

        if (!requestingUserCheck.rows[0]?.is_admin) {
            return res.status(403).json({ error: 'Only team admins can promote members' });
        }

        // Promote the member to admin
        await db.query(
            `UPDATE TeamMembers 
             SET is_admin = true 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, memberToPromoteId]
        );

        res.json({ message: 'Member promoted to admin successfully' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to promote member to admin' });
    }
};

exports.toggleAdminStatus = async (req, res) => {
    const { teamId, userId: memberId } = req.params;
    const { isAdmin } = req.body;
    const requestingUserId = req.user.id;

    try {
        // Check if requesting user is admin
        const requestingUserCheck = await db.query(
            `SELECT is_admin 
             FROM TeamMembers 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, requestingUserId]
        );

        if (!requestingUserCheck.rows[0]?.is_admin) {
            return res.status(403).json({ error: 'Only team admins can change admin status' });
        }

        // Update admin status
        await db.query(
            `UPDATE TeamMembers 
             SET is_admin = $1 
             WHERE team_id = $2 AND user_id = $3`,
            [isAdmin, teamId, memberId]
        );

        res.json({ message: 'Admin status updated successfully' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to update admin status' });
    }
};

exports.deleteTeam = async (req, res) => {
    const { teamId } = req.params;
    const requestingUserId = req.user.id;

    try {
        // Check if user is a company member
        const userRole = await db.query(
            'SELECT role FROM Users WHERE id = $1',
            [requestingUserId]
        );

        const isCompanyMember = userRole.rows[0]?.role === 'COMPANY_MEMBER';

        if (!isCompanyMember) {
            // If not a company member, check if user is team admin
            const requestingUserCheck = await db.query(
                `SELECT is_admin 
                 FROM TeamMembers 
                 WHERE team_id = $1 AND user_id = $2`,
                [teamId, requestingUserId]
            );

            if (!requestingUserCheck.rows[0]?.is_admin) {
                return res.status(403).json({ error: 'Only team admins or company members can delete teams' });
            }
        }

        await db.query('BEGIN');

        // Delete all sessions associated with the team
        await db.query(
            `DELETE FROM Sessions 
             WHERE team_id = $1`,
            [teamId]
        );

        // Delete all team members
        await db.query(
            `DELETE FROM TeamMembers 
             WHERE team_id = $1`,
            [teamId]
        );

        // Finally delete the team
        await db.query(
            `DELETE FROM Teams 
             WHERE id = $1`,
            [teamId]
        );

        await db.query('COMMIT');

        res.json({ message: 'Team deleted successfully' });
    } catch (err) {
        await db.query('ROLLBACK');
        res.status(500).json({ error: 'Failed to delete team: ' + err.message });
    }
};

exports.leaveTeam = async (req, res) => {
    const { teamId } = req.params;
    const userId = req.user.id;

    try {
        // Check if user is the last admin
        const adminCheck = await db.query(
            `SELECT COUNT(*) as admin_count 
             FROM TeamMembers 
             WHERE team_id = $1 AND is_admin = true`,
            [teamId]
        );

        const userCheck = await db.query(
            `SELECT is_admin 
             FROM TeamMembers 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, userId]
        );

        if (adminCheck.rows[0].admin_count === 1 && userCheck.rows[0]?.is_admin) {
            return res.status(400).json({
                error: 'Cannot leave team as last admin. Delete team instead.'
            });
        }

        // Remove user from team
        await db.query(
            `DELETE FROM TeamMembers 
             WHERE team_id = $1 AND user_id = $2`,
            [teamId, userId]
        );

        res.json({ message: 'Successfully left team' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to leave team' });
    }
};

exports.revertPremiumStatus = async (req, res) => {
    const { teamId } = req.params;

    try {
        const result = await db.query(`
            UPDATE Teams 
            SET is_premium = false,
                subscription_status = 'FREE',
                subscription_id = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING *`,
            [teamId]
        );

        if (result.rowCount === 0) {
            return res.status(404).json({ error: 'Team not found' });
        }

        res.json({ success: true, team: result.rows[0] });
    } catch (error) {
        res.status(500).json({ error: 'Database update failed' });
    }
};

exports.cancelSubscription = async (req, res) => {
    const { teamId } = req.params;
    
    try {
        // Get team's subscription ID
        const teamResult = await db.query(
            'SELECT subscription_id FROM Teams WHERE id = $1',
            [teamId]
        );

        const subscriptionId = teamResult.rows[0]?.subscription_id;
        if (!subscriptionId) {
            return res.status(400).json({ error: 'No active subscription found' });
        }

        // Cancel the subscription in Stripe
        const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
        await stripe.subscriptions.cancel(subscriptionId);

        // Update team status
        await db.query(`
            UPDATE Teams 
            SET is_premium = false,
                subscription_status = 'FREE',
                subscription_id = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1`,
            [teamId]
        );

        res.json({ message: 'Subscription cancelled successfully' });
    } catch (error) {
        res.status(500).json({ error: 'Failed to cancel subscription' });
    }
};

exports.createBillingPortalSession = async (req, res) => {
    const { teamId } = req.params;
    
    try {
        // Get team's subscription ID
        const teamResult = await db.query(
            'SELECT subscription_id FROM Teams WHERE id = $1',
            [teamId]
        );

        const subscriptionId = teamResult.rows[0]?.subscription_id;
        if (!subscriptionId) {
            return res.status(400).json({ error: 'No active subscription found' });
        }

        // Get customer ID from subscription
        const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
        const subscription = await stripe.subscriptions.retrieve(subscriptionId);
        
        // Create portal session with customer ID
        const session = await stripe.billingPortal.sessions.create({
            customer: subscription.customer,
            return_url: `${process.env.CLIENT_URL}/dashboard`,
        });

        res.json({ url: session.url });
    } catch (error) {
        console.error('Billing portal error:', error);
        res.status(500).json({ error: 'Failed to create billing portal session' });
    }
}; 