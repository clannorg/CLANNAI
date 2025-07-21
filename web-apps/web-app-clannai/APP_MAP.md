# Clann Football Analysis Platform - Application Map

## 1. Project Overview
- **Purpose:**  
  Clann is a comprehensive sports analysis platform focused on football. It enables teams and company analysts to upload game footage, receive AI-powered performance analysis (e.g., heatmaps, sprint maps, momentum graphs), and manage teams and sessions effectively.
  
- **Core Features:**
  - **Authentication & User Management:**  
    Email-based login/register using JWT; role-based access (Regular User, Team Admin, Company Analyst).
  - **Team Management:**  
    Create and join teams via unique codes; manage members, promotions, and premium account upgrades via Stripe.
  - **Session Analysis:**  
    Upload game footage URLs; process and store analysis images/videos (stored on AWS S3); track session status (PENDING/REVIEWED).
  - **Company Dashboard:**  
    A dedicated dashboard for analysts to view, filter, and manage sessions, including direct analysis uploads.

- **Usage Scenarios:**
  - Regular users upload footage and view automated analysis.
  - Team admins manage their teams and invite new members.
  - Company users (analysts) review all sessions, add further analysis, and update statuses.

## 2. Architecture & Project Structure
- **Directory Structure:**
  - **client/** – React application (pages like Login, Profile, Sessions, Company Dashboard; components like SessionCard, TeamCard, StatsOverview).
  - **server/** – Node.js/Express API (routes for auth, sessions, teams, payments; controllers and middleware for logging, error handling, and file uploads).
  - **docs/** – Technical documentation (tech stack, user flows, API specifications, deployment guides).
  - Supporting files in the root such as `README.md`, `TASKS.md`, and database definition files.

- **Technology Stack:**
  - **Frontend:** React, Tailwind CSS, and supporting libraries (e.g., recharts, react-router-dom).
  - **Backend:** Node.js with Express, JWT-based authentication.
  - **Database & Cloud:** PostgreSQL (AWS RDS), AWS S3 for media, AWS Amplify for deployment.
  - **Payments:** Stripe integration for handling premium upgrades.
  - **DevOps:** Suggestions toward using a monorepo strategy for unified code management and deployments.

## 3. Components & Modules
- **Frontend Components:**
  - **Pages:** Login, Profile, Sessions, Company Dashboard, and Terms & Conditions.
  - **UI Elements:** SessionCard, TeamCard, TeamMembersModal, StatsOverview.
  - **Service Layers:** Modules for handling API calls for authentication, sessions, teams, and user management.

- **Backend Modules:**
  - **API Routes:**  
    - `/api/auth` – User authentication and session management.  
    - `/api/sessions` – Create, update, and fetch session details (including analysis uploads).  
    - `/api/teams` – Manage team creation, join codes, and member roles.  
    - `/api/payments` – Stripe checkout and webhook handling.
  - **Controllers & Utilities:**  
    Handle business logic (data validation, file uploads, normalization of metrics) and static file serving (for analysis images).

- **Third-Party Integrations:**
  - **Stripe:** For payment processing and subscription management.
  - **AWS:** S3 for media storage, Amplify for hosting & CI/CD pipelines.

## 4. Data Flow & Models
- **Data Flow:**
  - Users authenticate and receive a JWT that is used to access secured endpoints.
  - Game footage URLs are submitted to create session records.
  - Analysis images and videos are uploaded via dedicated endpoints, stored in AWS S3, and their URLs saved in the database.
  - Sessions are linked to teams and users (uploaders and reviewers).

- **Data Models & Relationships:**
  - **Users:** Maintain email, password hash, role, and timestamps.
  - **Teams:** Include team name, unique team code, subscription status, and trial end date.
  - **Sessions:** Store footage URLs, analysis media (images/videos), status fields, and relationship references (team_id, uploaded_by).
  - **Relationships:**  
    - Users and Teams are connected via a many-to-many mapping (TeamMembers).  
    - Teams have many Sessions; Sessions reference both the uploader and the reviewer.

## 5. API Endpoints & Integration
- **Key Endpoints:**
  - **GET /api/sessions/all:**  
    Retrieves all session records for the company dashboard.
  - **POST /api/sessions/analysis:**  
    Handles file uploads for analysis images/videos.
  - **DELETE /api/sessions/{sessionId}/analysis/{type}:**  
    Deletes a specific analysis asset.
  - **PUT /api/sessions/{sessionId}/status:**  
    Updates the status of a session (e.g., from PENDING to REVIEWED).
  - **PUT /api/sessions/{sessionId}/description:**  
    Updates analysis descriptions.
  - **Stripe Endpoints:**  
    For creating checkout sessions and handling webhook events.
  
- **Authentication & Security:**  
  All endpoints require proper authorization headers with JWT tokens and additional validations where applicable.

## 6. User Flows & UI/UX Patterns
- **Regular User Flow:**
  - Register or login.
  - Upload game footage URL and automatically create a session (first upload makes the user a team admin).
  - View analysis results including performance metrics and visualizations.
  
- **Team Admin Flow:**
  - In addition to regular user features, manage team members (remove/promote), and share unique team access codes.
  
- **Company (Analyst) Flow:**
  - Access a comprehensive dashboard to review all sessions.
  - Filter and sort sessions; upload additional analysis (images/videos) and update session statuses.
  
- **UI/UX Considerations:**
  - Responsive grid layouts and card designs (e.g., SessionCard) for clarity.
  - Real-time feedback on uploads and status toggling.
  - Consistent navigation using React Router and clear call-to-action buttons.

## 7. Environment & Deployment
- **Deployment Configurations:**
  - **AWS Amplify:**  
    Utilized for hosting and CI/CD pipelines.
  - **Environment Variables:**  
    Must be set in the `.env` file (e.g., DATABASE_URL, JWT_SECRET, STRIPE_SECRET_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY).
  - **Static Asset Serving:**  
    Express serves analysis images from designated directories in both public and storage folders.
  
- **Monorepo & DevOps:**  
  The suggested monorepo structure allows unified management of all code (frontend, backend, additional services) and centralized deployment monitoring via platforms like Devopness.

## 8. Testing, Logging & Debugging
- **Frontend Testing:**  
  Unit and integration tests are implemented using Jest and React Testing Library.
  
- **Backend Testing:**  
  API endpoints are tested for functionality and security.
  
- **Logging & Error Handling:**  
  - Express middleware logs incoming requests and errors.
  - Dedicated error-handling middleware provides standardized JSON responses.
  - Debug features (e.g., video header debugging) help in pinpointing issues during development.

## 9. Known Issues & Future Plans
- **Known Issues:**
  - Occasional UI glitches (e.g., video playback issues in some browsers).
  - File upload error handling improvements needed.
  
- **Future Enhancements:**
  - Integration of enhanced data visualization (e.g., spider charts) for session details.
  - Further refinements of team customization (logo upload, color theming).
  - Expanded payment features and further Stripe integration (trial offers, batch updates).
  - Transition toward a full monorepo structure for better visibility and management of all services.

## 10. Additional Context
- **Historical Decisions:**
  - The project evolved through distinct phases: initial authentication and navigation, through iterative enhancements in team and session management, culminating in an integrated company dashboard.
  - Architectural recommendations (e.g., the monorepo approach) have been incorporated based on team feedback.
  
- **References & Documentation:**
  - See `README.md` for overarching project vision and quick start instructions.
  - Detailed technical documents reside in `docs/project/` (tech stack, API specs, user flows).
  - User journey and task prioritizations are outlined in `user-flows.txt` and `TASKS.md`. 