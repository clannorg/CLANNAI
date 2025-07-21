const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../../server/.env') });

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
    ssl: {
        rejectUnauthorized: false
    }
});

async function updateSessionMetrics() {
    try {
        // 1. Add new session_data column
        await pool.query(`
            ALTER TABLE Sessions 
            ADD COLUMN session_data JSONB DEFAULT '{
                "match_info": {
                    "team1": {
                        "name": "",
                        "metrics": {
                            "total_distance": 0,
                            "sprint_distance": 0,
                            "total_sprints": 0,
                            "avg_sprint_speed": 0,
                            "energy": 0
                        }
                    },
                    "team2": {
                        "name": "",
                        "metrics": {
                            "total_distance": 0,
                            "sprint_distance": 0,
                            "total_sprints": 0,
                            "avg_sprint_speed": 0,
                            "energy": 0
                        }
                    },
                    "score": {
                        "team1": 0,
                        "team2": 0
                    }
                }
            }'::jsonb;
        `);

        // 2. Migrate existing data
        await pool.query(`
            UPDATE Sessions 
            SET session_data = jsonb_build_object(
                'match_info', jsonb_build_object(
                    'team1', jsonb_build_object(
                        'name', (SELECT name FROM Teams WHERE id = team_id),
                        'metrics', jsonb_build_object(
                            'total_distance', COALESCE((team_metrics->>'total_distance')::numeric, 0),
                            'sprint_distance', COALESCE((team_metrics->>'sprint_distance')::numeric, 0),
                            'total_sprints', COALESCE((team_metrics->>'total_sprints')::numeric, 0),
                            'avg_sprint_speed', COALESCE((team_metrics->>'top_sprint_speed')::numeric, 0),
                            'energy', 0
                        )
                    ),
                    'team2', jsonb_build_object(
                        'name', 'Unknown',
                        'metrics', jsonb_build_object(
                            'total_distance', 0,
                            'sprint_distance', 0,
                            'total_sprints', 0,
                            'avg_sprint_speed', 0,
                            'energy', 0
                        )
                    ),
                    'score', jsonb_build_object(
                        'team1', 0,
                        'team2', 0
                    )
                )
            );
        `);

        console.log('Successfully updated session metrics structure');
    } catch (error) {
        console.error('Error:', error);
    } finally {
        await pool.end();
    }
}

updateSessionMetrics();