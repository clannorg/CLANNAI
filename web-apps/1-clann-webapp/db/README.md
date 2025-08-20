# 🗄️ Database Setup

## Current Setup (AWS RDS Production)

**⚠️ WARNING: This project uses AWS RDS production database directly for development!**

- Database: AWS RDS PostgreSQL
- Host: `clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com`
- Database: `postgres`
- User: `postgres`

## Environment Variables

Your backend `.env` file should contain:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres
DB_HOST=clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

## Database Structure

Current tables:
- `users` - User accounts (regular/company roles)
- `teams` - Football teams with colors/logos
- `team_members` - User-team relationships
- `games` - Video games with AI analysis data

Key JSONB columns:
- `games.ai_analysis` - AI-generated events (goals, passes, etc.)
- `games.tactical_analysis` - Tactical analysis data
- `games.metadata` - Additional game metadata

## Useful Commands

### Connect to Database
```bash
psql 'postgresql://postgres:YOUR_PASSWORD@clann-webapp-prod.cfcgo2cma4or.eu-west-1.rds.amazonaws.com:5432/postgres'
```

### Check Table Structure
```sql
\d+ games
\d+ teams
\d+ users
```

### Common Queries
```sql
-- Check games with AI analysis
SELECT title, status, ai_analysis IS NOT NULL as has_analysis FROM games;

-- Check team structure
SELECT name, team_code FROM teams;

-- View game events count
SELECT title, jsonb_array_length(ai_analysis) as event_count FROM games WHERE ai_analysis IS NOT NULL;
```

## Scripts

Use the scripts in `/db/scripts/` to inspect data:
- `checkGreenislandEvents.js` - Check specific game events
- `listGamesWithEnv.js` - List all games with metadata
- `analyzeCookstownS3.js` - Analyze S3 data for games

## Migration Strategy

**⚠️ CAUTION: This is production data!**

1. Create migration file in `migrations/`
2. Test on a database backup first
3. Use existing JSONB columns when possible (safer than schema changes)
4. Consider using `metadata` column for new features

## Current Issues

- No separate dev/staging environment
- Schema changes require production database modifications
- Mixed local/production setup can cause confusion 