# Database Scripts Guide

## Successful Script Structure
For database modification scripts to work correctly, use this template:

```javascript
const { Pool } = require("pg");
const path = require('path');
require("dotenv").config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: { rejectUnauthorized: false }
});
```

## Key Components

1. **Path Resolution**
   - Use `path.join(__dirname, '../../../server/.env')`
   - This correctly locates .env file from any script location
   - Prevents path resolution issues across different environments

2. **Database Connection**
   - Use individual connection parameters (not DATABASE_URL)
   - Include all required pool settings
   - Keep SSL config simple: `ssl: { rejectUnauthorized: false }`

3. **Error Handling**
```javascript
try {
    await pool.query(`YOUR QUERY HERE`);
    console.log('Success message');
} catch (error) {
    console.error('Error:', error);
} finally {
    await pool.end();
}
```

## Common Issues & Solutions

1. **Connection Errors**
   - Wrong .env path → Use path.join
   - SSL issues → Use simplified SSL config
   - Connection timeout → Check VPN/network

2. **Permission Errors**
   - For ALTER TABLE operations
   - For INSERT/UPDATE operations
   - Solution: Ensure correct DB user permissions

## Best Practices

1. Always close pool connection in finally block
2. Log both success and error messages
3. Use COALESCE for NULL handling in JSONB
4. Test scripts locally before production
5. Back up data before running ALTER scripts

## Example Scripts
- printDbContent.js: View database content
- updateSessionMetrics.js: Modify table structure
- addSubscriptionColumns.js: Add new columns 