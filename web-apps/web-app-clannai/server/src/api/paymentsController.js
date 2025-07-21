const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const db = require('../db');

exports.createPaymentIntent = async (req, res) => {
    const { teamId } = req.body;

    try {
        // Create a payment intent
        const paymentIntent = await stripe.paymentIntents.create({
            amount: 1000, // Amount in cents
            currency: 'usd',
            metadata: { teamId }
        });

        res.json({ clientSecret: paymentIntent.client_secret });
    } catch (error) {
        console.error('Error creating payment intent:', error);
        res.status(500).json({ error: 'Failed to create payment intent' });
    }
}; 