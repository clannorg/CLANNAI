# 🗄️ Database Setup

## Prerequisites

- PostgreSQL 15+ installed
- `createdb` and `psql` commands available
- Admin access to create databases

## Setup Instructions

### 1. Create Database
```bash
# Create the database
createdb clann_mvp

# Verify database exists
psql -l | grep clann_mvp
```

### 2. Run Schema
```bash
# Apply the schema
psql clann_mvp < schema.sql

# Verify tables created
psql clann_mvp -c "\dt"
```

### 3. Load Demo Data (Optional)
```bash
# Load demo teams and games
psql clann_mvp < seeds/demo_data.sql

# Verify data loaded
psql clann_mvp -c "SELECT COUNT(*) FROM teams;"
psql clann_mvp -c "SELECT COUNT(*) FROM games;"
```

## Environment Variables

Add to your backend `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/clann_mvp
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clann_mvp
DB_USER=your_username
DB_PASSWORD=your_password
```

## Useful Commands

### Connect to Database
```bash
psql clann_mvp
```

### Reset Database
```bash
psql clann_mvp < schema.sql
```

### Check Table Structure
```sql
\d+ users
\d+ teams
\d+ team_members
\d+ games
```

### View Demo Data
```sql
SELECT name, team_code FROM teams;
SELECT title, status FROM games;
```

## Migration Strategy

For future schema changes:

1. Create migration file in `migrations/`
2. Name format: `YYYY-MM-DD_description.sql`
3. Include both UP and DOWN operations
4. Test on development first

## Backup & Restore

### Backup
```bash
pg_dump clann_mvp > backup.sql
```

### Restore
```bash
psql clann_mvp < backup.sql
``` 