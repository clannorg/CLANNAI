# 💳 ClannAI Stripe Payment Integration Plan

**Status:** Planning Phase - Not Immediate Priority  
**Goal:** Complete payment system for premium team subscriptions  
**Source:** Copy proven system from `web-app-clannai` (already live on Devopness)  
**Timeline:** 4-6 hours when ready to implement  
**Complexity:** Medium-High (database changes + complete payment flow)

---

## 🎯 **INTEGRATION OVERVIEW**

**Why Not Immediate:** Core join/demo features are working perfectly  
**Why Later:** Payment system requires careful testing and database migrations  
**Benefit:** Monetize existing user base when ready for revenue  

**Current State:**  
✅ **Old App:** Complete working Stripe integration on `api.clannai.com`  
❌ **New App:** Zero payment infrastructure  

**Target State:**  
✅ Team premium upgrades with Stripe Checkout  
✅ 7-day trial periods  
✅ Subscription management  
✅ Webhook-based automatic upgrades  

---

## 📋 **PHASE 1: Dependencies & Environment** ⚡ *30 minutes*

### Backend Dependencies
```bash
cd 1-clann-webapp/backend
npm install stripe@^17.4.0
```

### Frontend Dependencies  
```bash
cd 1-clann-webapp/frontend
npm install @stripe/stripe-js@^5.2.0
```

### Environment Variables Setup
**Add to Devopness Variables for Backend:**
```bash
# Copy from your existing Devopness old app settings
STRIPE_SECRET_KEY=sk_live_[YOUR_STRIPE_SECRET_KEY]
STRIPE_WEBHOOK_SECRET=whsec_[YOUR_WEBHOOK_SECRET]  
STRIPE_PRICE_ID=price_[YOUR_PRICE_ID]
```

**Add to Frontend Environment:**
```bash
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_[YOUR_STRIPE_PUBLIC_KEY]
```

**⚠️ CRITICAL:** Fix Price ID mismatch between server/client in old app first.

---

## 📋 **PHASE 2: Database Schema Changes** ⚡ *45 minutes*

### Schema Migration SQL
```sql
-- Add to existing teams table
ALTER TABLE teams ADD COLUMN is_premium BOOLEAN DEFAULT false;
ALTER TABLE teams ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'FREE';
ALTER TABLE teams ADD COLUMN subscription_id VARCHAR(255);
ALTER TABLE teams ADD COLUMN trial_ends_at TIMESTAMP;
ALTER TABLE teams ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create indexes for performance
CREATE INDEX idx_teams_premium ON teams(is_premium);
CREATE INDEX idx_teams_subscription ON teams(subscription_status);
CREATE INDEX idx_teams_subscription_id ON teams(subscription_id);

-- Verify changes
\d teams
```

### Files to Create:
- [ ] `db/migrations/add_subscription_fields.sql`
- [ ] `db/migrations/add_subscription_indexes.sql`

---

## 📋 **PHASE 3: Backend Payment Infrastructure** ⚡ *2-3 hours*

### Files to Copy from `web-app-clannai/server/src/`:

#### 1. Payment Controllers
- [ ] **Copy:** `api/paymentsController.js` → `backend/routes/payments.js`
- [ ] **Copy:** `api/webhooksController.js` → `backend/routes/webhooks.js` 

#### 2. Stripe Integration in Main Server
**Modify:** `backend/server.js`
```javascript
// Add Stripe integration
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Add webhook endpoint (BEFORE express.json())
app.use('/api/webhook', express.raw({type: 'application/json'}), webhookRoutes);

// Add payment routes
app.use('/api/payments', paymentRoutes);
app.use('/api/create-checkout-session', checkoutRoutes);
```

#### 3. Team Controller Updates
**Modify:** `backend/routes/teams.js`
- [ ] Add premium check functions
- [ ] Add subscription cancellation
- [ ] Add billing portal access

### New Files to Create:
- [ ] `backend/routes/checkout.js` - Stripe checkout session creation
- [ ] `backend/middleware/premiumCheck.js` - Premium feature gating
- [ ] `backend/utils/stripe.js` - Stripe helper functions

---

## 📋 **PHASE 4: Frontend Payment UI** ⚡ *1-2 hours*

### Files to Copy from `web-app-clannai/client/src/`:

#### 1. Stripe Configuration
- [ ] **Copy:** `config/stripe.js` → `frontend/src/lib/stripe.js`

#### 2. Payment Components  
- [ ] **Copy:** `components/SubscriptionManager.js` → `frontend/src/components/SubscriptionManager.tsx`
- [ ] **Copy:** `pages/Success.js` → `frontend/src/app/success/page.tsx`
- [ ] **Copy:** `pages/Cancel.js` → `frontend/src/app/cancel/page.tsx`

#### 3. Dashboard Integration
**Modify:** `frontend/src/app/dashboard/page.tsx`
- [ ] Add "Upgrade to Premium" button
- [ ] Add subscription status display
- [ ] Add premium features gating

#### 4. Team Profile Updates
**Create:** `frontend/src/components/PremiumUpgrade.tsx`
- [ ] Stripe checkout button
- [ ] Trial period display  
- [ ] Subscription management

### New Components to Create:
- [ ] `frontend/src/components/PaymentButton.tsx`
- [ ] `frontend/src/components/PremiumBadge.tsx`  
- [ ] `frontend/src/components/BillingPortal.tsx`

---

## 📋 **PHASE 5: Testing & Deployment** ⚡ *1 hour*

### Local Testing Checklist:
- [ ] Stripe CLI webhook forwarding: `stripe listen --forward-to localhost:3002/api/webhook`
- [ ] Test successful payment flow
- [ ] Test webhook database updates
- [ ] Test subscription cancellation
- [ ] Test premium feature access

### Production Deployment:
- [ ] Configure webhook endpoint in Stripe Dashboard
- [ ] Test live payment flow
- [ ] Verify webhook signature validation
- [ ] Monitor error logs

---

## 🚨 **CRITICAL CONSIDERATIONS**

### 1. Price ID Configuration
**Important:** Server and Client must use the same Stripe Price ID
- Verify Price ID consistency across environments
- Check existing old app configuration for reference

### 2. Database Migration Safety
- [ ] Backup production database before schema changes
- [ ] Test migration on staging environment first
- [ ] Plan rollback strategy

### 3. Webhook Security
- [ ] Verify webhook signature validation
- [ ] Use raw body parser for webhooks only  
- [ ] Monitor webhook failure rates

### 4. Error Handling
- [ ] Payment failure UI states
- [ ] Webhook retry logic
- [ ] Subscription status sync verification

---

## 🎯 **PREMIUM FEATURES TO GATE**

Once payment system is live, these features can become premium:

### Team Features:
- [ ] **Multiple team management** (free = 1 team, premium = unlimited)
- [ ] **Advanced analytics** (heat maps, advanced stats)  
- [ ] **Custom team branding** (logos, colors)
- [ ] **Video upload/storage** (free = demo only, premium = upload)

### Analysis Features:  
- [ ] **AI coaching insights** (free = basic, premium = detailed)
- [ ] **Export capabilities** (PDF reports, data export)
- [ ] **Priority support** (premium users get faster support)

---

## 💰 **BUSINESS MODEL**

**Pricing Strategy:** (Based on existing Stripe setup)
- **Free Tier:** Demo content access, 1 team, basic features
- **Premium Tier:** $10/month, unlimited teams, all features, 7-day trial

**Revenue Readiness:**
- ✅ Payment infrastructure ready to copy
- ✅ Live Stripe account configured  
- ✅ User base growing with join codes
- ✅ Demo content proves value proposition

---

## 🚀 **WHEN TO IMPLEMENT**

**Ready When:**
- [ ] User base reaches 50+ active teams
- [ ] Core features are fully stable
- [ ] Customer feedback indicates willingness to pay
- [ ] Support system is ready for billing questions

**Success Metrics Post-Launch:**
- [ ] 5% trial-to-paid conversion rate
- [ ] <2% monthly churn rate  
- [ ] Zero payment processing errors
- [ ] Customer satisfaction >4.5/5

---

*This plan leverages your existing, battle-tested Stripe integration from the old app. When ready to implement, this provides a complete roadmap for adding professional payment capabilities to your new ClannAI platform.*

## 📝 **IMPLEMENTATION NOTES**

- All sensitive API keys and secrets should be stored in your local SENSITIVE_IMPLEMENTATION_DETAILS.md file (gitignored)
- Reference your existing Devopness configuration for the actual credential values
- Test thoroughly in staging environment before production deployment