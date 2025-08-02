const express = require("express");
const router = express.Router();
const teamsController = require("./teamsController");
const auth = require("../middleware/auth");
const db = require('../db');

router.get("/user", auth, teamsController.getUserTeams);
router.post("/create", auth, teamsController.createTeam);
router.post('/join', auth, teamsController.joinTeam);
router.get("/:teamId/members", auth, async (req, res) => {
    console.log('Team members request received for teamId:', req.params.teamId);
    try {
        const { teamId } = req.params;
        const members = await db.query(`
            SELECT 
                u.email,
                u.id as user_id,
                tm.is_admin
            FROM TeamMembers tm
            JOIN Users u ON tm.user_id = u.id
            WHERE tm.team_id = $1
            ORDER BY tm.is_admin DESC, u.email
        `, [teamId]);

        console.log('Team members found:', members.rows);
        res.json(members.rows);
    } catch (err) {
        console.error('Error in team members route:', err);
        res.status(500).json({ error: 'Failed to fetch team members' });
    }
});
router.delete("/:teamId/members/:userId", auth, teamsController.removeTeamMember);
router.patch("/:teamId/members/:userId/promote", auth, teamsController.promoteToAdmin);
router.patch("/:teamId/members/:userId/admin", auth, teamsController.toggleAdminStatus);
router.delete("/:teamId", auth, teamsController.deleteTeam);

// Team color management routes
router.get("/:teamId/colors", auth, teamsController.getTeamColors);
router.put("/:teamId/colors", auth, teamsController.updateTeamColors);

module.exports = router;