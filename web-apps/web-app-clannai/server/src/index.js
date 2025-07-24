require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const authRoutes = require('./api/auth');
const sessionsRoutes = require('./api/sessions');
const teamsRoutes = require('./api/teams');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const successRoute = require('./api/success');
const webhooksController = require('./api/webhooksController');
const teamsController = require('./api/teamsController');
const db = require('./db');

const app = express();

// Webhook endpoint needs raw body - MUST BE FIRST
app.post('/api/webhook',
    express.raw({ type: 'application/json' }),
    webhooksController.handleStripeWebhook
);

// THEN other middleware
app.use(cors({
    origin: process.env.CLIENT_URL,
    credentials: true
}));
app.use(express.json());

// Register the checkout endpoint
app.post('/api/create-checkout-session', async (req, res) => {
    console.log('🔔 CREATE CHECKOUT SESSION CALLED:', { teamId: req.body.teamId });
    
    const { teamId } = req.body;
    console.log('👉 Team ID:', teamId);
    try {
        const teamResult = await db.query(
            'SELECT is_premium, subscription_status FROM Teams WHERE id = $1',
            [teamId]
        );
        
        console.log('👉 Team query result:', teamResult.rows[0]);

        if (teamResult.rows[0]?.is_premium) {
            console.log('❌ Team already premium:', teamId);
            return res.status(400).json({ 
                error: 'Team already has an active subscription' 
            });
        }

        console.log('👉 Creating Stripe session...');
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            client_reference_id: teamId,
            line_items: [{
                price: process.env.STRIPE_PRICE_ID,
                quantity: 1,
            }],
            mode: 'subscription',
            subscription_data: {
                trial_period_days: 7,
                metadata: {
                    teamId: teamId,
                    source: 'checkout'
                }
            },
            metadata: {
                teamId: teamId,
                source: 'checkout'
            },
            success_url: `${process.env.CLIENT_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${process.env.CLIENT_URL}/cancel`,
        });
        console.log('✅ Stripe session created');

        console.log('👉 Updating team in database...');
        // const updateResult = await db.query(
        //     'UPDATE Teams SET is_premium = true, subscription_status = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
        //     ['active', teamId]
        // );
        // console.log('✅ Team update result:', updateResult.rows[0]);


        console.log("JJJJJJJJJJ")


        console.log('✅ STRIPE SESSION CREATED AND TEAM UPDATED:', {
            sessionId: session.id,
            teamId: teamId,
            successUrl: session.success_url,
            cancelUrl: session.cancel_url,
            premiumStatus: 'active'
        });

        res.json({ id: session.id });
    } catch (error) {
        console.error('💥 STRIPE ERROR:', error);
        res.status(500).json({ error: error.message });
    }
});

app.use('/analysis-images', express.static(path.join(__dirname, '../public/analysis-images')));
app.use('/analysis-images', express.static(path.join(__dirname, '../storage/analysis-images')));

// Serve React build files (including videos, images, etc.)
// Add debugging and explicit MIME type handling
app.use((req, res, next) => {
    console.log('Static request:', req.url);
    next();
});

app.use(express.static(path.join(__dirname, '../client/build'), {
    setHeaders: (res, path) => {
        console.log('Serving static file:', path);
        if (path.endsWith('.mp4')) {
            res.setHeader('Content-Type', 'video/mp4');
        }
    }
}));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/sessions', sessionsRoutes);
app.use('/api/teams', teamsRoutes);
app.use('/api', successRoute);

app.post('/teams/:teamId/revert-premium', teamsController.revertPremiumStatus);
app.post('/api/teams/:teamId/billing-portal', (req, res, next) => {
    console.log('🎯 Billing portal route hit:', req.params);
    teamsController.createBillingPortalSession(req, res, next);
});

// Catch-all handler: send back React's index.html file for any non-API routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/build/index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {});
