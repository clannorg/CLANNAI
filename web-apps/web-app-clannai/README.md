# First, let's update the README
cat > README.md << 'EOL'
# Sports Analysis Platform

## Core Features
1. Authentication & User Management
   - Login/Register with email
   - Role-based access (User, Admin, Company)
   - Terms & Conditions acceptance

2. Team Management
   - Create/Join teams via codes
   - Member management
   - Premium upgrades via Stripe
   - Admin controls

3. Session Analysis
   - Game footage upload
   - AI-powered analysis
   - Performance metrics
   - Visual analysis (heatmaps, sprint maps)

4. Company Dashboard
   - Session review system
   - Analysis management
   - Status tracking

## Tech Stack
- Frontend: React, Tailwind CSS
- Backend: Node.js, Express
- Database: PostgreSQL
- Cloud: AWS S3
- Payments: Stripe
- Authentication: JWT

## Development
\`\`\`bash
npm install    # Install dependencies
npm run dev    # Start development server
\`\`\`

## Environment Variables
Required in .env:
- DATABASE_URL
- JWT_SECRET
- STRIPE_SECRET_KEY
- AWS_ACCESS_KEY
- AWS_SECRET_KEY