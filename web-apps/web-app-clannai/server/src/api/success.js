const express = require('express');
const router = express.Router();

router.get('/success', (req, res) => {
    // Use environment variable for client URL
    const clientUrl = process.env.REACT_APP_CLIENT_URL || 'http://localhost:3002';
    res.redirect(`${clientUrl}/success`);
});

module.exports = router; 