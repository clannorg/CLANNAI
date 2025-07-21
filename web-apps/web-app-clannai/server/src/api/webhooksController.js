const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const db = require('../db');

exports.handleStripeWebhook = async (req, res) => {
    console.log('⚡️ Webhook request received:', {
        eventType: req.body?.type,
        hasSignature: !!req.headers['stripe-signature']
    });
    const sig = req.headers['stripe-signature'];
    let event;

    console.log('💰 Webhook received:', {
        headers: req.headers,
        signaturePresent: !!sig,
        bodyType: typeof req.body,
        bodyLength: req.body.length,
        timestamp: new Date().toISOString()
    });

    try {
        event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
        console.log('🎣 Webhook event received:', {
            type: event.type,
            data: event.data.object,
            metadata: event.data.object.metadata || {},
            subscription: event.data.object.subscription || event.data.object.id
        });

        if (event.type === 'customer.subscription.created') {
            const subscription = event.data.object;
            // Log the full subscription object
            console.log('📦 Subscription data:', subscription);
            
            // Get teamId from metadata
            const teamId = subscription.metadata.teamId || subscription.client_reference_id;
            console.log('🎯 Team ID found:', teamId);

            try {
                const result = await db.query(`
                    UPDATE Teams 
                    SET is_premium = true,
                        subscription_status = 'PREMIUM',
                        subscription_id = $1,
                        trial_ends_at = CURRENT_TIMESTAMP + INTERVAL '7 days',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                    RETURNING *`,
                    [subscription.id, teamId]
                );

                console.log('💾 Database update result:', {
                    success: result.rowCount > 0,
                    updatedTeam: result.rows[0]
                });

                if (result.rowCount === 0) {
                    console.error('❌ No team found with ID:', teamId);
                }
            } catch (dbError) {
                console.error('❌ Database error:', dbError);
                throw dbError;
            }
        }

        return res.status(200).json({ received: true });
    } catch (err) {
        console.error('❌ Webhook Error:', {
            message: err.message,
            stack: err.stack,
            event: event?.type,
            data: event?.data?.object
        });
        return res.status(400).json({ error: `Webhook Error: ${err.message}` });
    }
}; 