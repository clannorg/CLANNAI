# Navigate to docs/project directory
mkdir -p docs/project

# Create the stripe-integration.md file
cat > docs/project/stripe-integration.md << 'EOL'
# Stripe Integration Documentation

## Overview
Payment processing system using Stripe Checkout and webhooks for team premium upgrades.

## Key Components

### 1. Frontend Payment Flow
- User clicks "Upgrade" button on team profile
- Creates checkout session via API
- Redirects to Stripe hosted checkout page
- Success/cancel pages handle redirect

### 2. Server Endpoints

#### Checkout Session Creation
- `/create-checkout-session` endpoint
- Requires teamId
- Creates Stripe checkout session
- Returns session ID

#### Webhook Handler
- `/webhook` endpoint (raw body parser)
- Verifies Stripe signature
- Processes checkout.session.completed events
- Updates team premium status in database

## Database Schema
Teams table premium columns:
- is_premium (boolean)
- subscription_status (FREE/TRIAL/PREMIUM) 
- subscription_id (Stripe reference)
- trial_ends_at (timestamp)
- updated_at (timestamp)

## Webhook Infrastructure

### Local Development
1. Install Stripe CLI
2. Run `stripe listen --forward-to localhost:3001/webhook`
3. Add webhook secret to .env
4. Test with `stripe trigger checkout.session.completed`

### Production
1. Configure webhook endpoint in Stripe Dashboard
2. Set webhook secret in environment variables
3. Enable relevant event types (checkout.session.completed)

## Security Considerations
1. Webhook signature verification
2. Raw body parsing for webhooks
3. Environment variable security
4. CORS configuration

## Error Handling
1. Signature verification failures
2. Database update errors
3. Invalid team IDs
4. Payment processing errors

## Testing
1. Use Stripe CLI for local webhook testing
2. Test successful payments
3. Verify database updates
4. Check error scenarios

## Required Environment Variables
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
CLIENT_URL=http://localhost:3002


## Common Issues
1. Missing webhook secret
2. Incorrect webhook signature
3. Database transaction failures
4. Missing environment variables

## Monitoring
1. Webhook event logs
2. Payment success/failure rates
3. Database update confirmations
4. Error tracking and alerts
EOL

# Verify the file was created
cat docs/project/stripe-integration.md