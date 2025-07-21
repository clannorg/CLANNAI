COMPANY USER DATA ACCESS FLOW
============================

1. INITIAL DISPLAY (Dashboard.js)
--------------------------------
Location: client/src/pages/company/Dashboard.js
- Company user sees buttons: "Sessions", "Team Management", "Database Overview"
- When "Team Management" is clicked: setActiveView('teams')
- This renders <TeamsList /> component

2. FRONTEND REQUEST (TeamList.js)
--------------------------------
Location: client/src/components/dashboard/TeamList.js
- Component mounts and runs useEffect
- Calls teamService.getTeamsWithValidSessions()

3. API SERVICE LAYER (teamService.js)
------------------------------------
Location: client/src/services/teamService.js
- Makes authenticated API call using:
  api.get('/sessions/teams-with-valid-sessions')
- API instance automatically includes auth token from localStorage

4. BACKEND ROUTE (sessions.js)
-----------------------------
Location: server/src/api/sessions.js
- Receives request at: GET /api/sessions/teams-with-valid-sessions
- Protected by auth middleware
- Routes to sessionsController.getTeamsWithValidSessions

5. DATABASE QUERY (sessionsController.js)
----------------------------------------
Location: server/src/api/sessionsController.js
- Executes SQL query:
  ```sql
  SELECT DISTINCT 
      t.id,
      t.name,
      t.team_code,
      t.created_at,
      t.subscription_status,
      COUNT(s.id) as valid_session_count
  FROM Teams t
  INNER JOIN Sessions s ON t.id = s.team_id
  WHERE (s.footage_url LIKE '%veo.co%' OR s.footage_url LIKE '%youtu%')
      AND s.footage_url IS NOT NULL
      AND s.footage_url != ''
  GROUP BY t.id, t.name, t.team_code
  ORDER BY valid_session_count DESC
  ```
- Returns results as JSON

6. DATA DISPLAY (TeamList.js)
----------------------------
Location: client/src/components/dashboard/TeamList.js
- Receives data and maps it to JSX
- Displays each team with:
  - Team name
  - Team code
  - Creation date
  - Valid session count
  - View/Delete options

SECURITY MEASURES
----------------
1. Frontend:
   - Auth token required for API calls
   - Stored in localStorage after login
   - Included automatically by api.js service

2. Backend:
   - auth middleware checks token validity
   - Only company users can access these routes
   - Database queries are parameterized

FILE DEPENDENCIES
----------------
Frontend:
- Dashboard.js
- TeamList.js
- teamService.js
- api.js (for auth)

Backend:
- sessions.js (routes)
- sessionsController.js (db queries)
- auth.js (middleware)
- db.js (database connection) 

