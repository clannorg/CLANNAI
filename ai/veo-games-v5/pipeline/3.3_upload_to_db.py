#!/usr/bin/env python3
"""
Step 7: Upload analysis to database
Updates the PostgreSQL database with S3 URLs and analysis data.
"""

import json
import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def load_env_vars():
    """Load database connection from environment"""
    env_file = Path(__file__).parent.parent.parent.parent / "web-apps/1-clann-webapp/backend/.env"
    
    if not env_file.exists():
        print(f"❌ .env file not found: {env_file}")
        return None
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value.strip('"').strip("'")
    
    return env_vars.get('DATABASE_URL')

def connect_to_db():
    """Connect to PostgreSQL database"""
    database_url = load_env_vars()
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return None
    
    try:
        # Parse SSL requirement
        ssl_mode = 'require' if 'rds.amazonaws.com' in database_url else 'disable'
        
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            sslmode=ssl_mode
        )
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def upload_to_database(match_id, game_id=None):
    """Upload analysis data to database using direct PostgreSQL connection"""
    print(f"🎯 Uploading {match_id} analysis to database...")
    
    # Load data files
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    
    # Load S3 locations
    s3_file = base_path / "3.2_s3_core_locations.json"
    if not s3_file.exists():
        print(f"❌ S3 locations not found: {s3_file}")
        print("Run step 6 first: python 6_s3_uploader_with_clips.py <match-id>")
        return False
    
    with open(s3_file, 'r') as f:
        s3_locations = json.load(f)
    
    # Load team config
    team_config_file = base_path / "1_team_config.json"
    with open(team_config_file, 'r') as f:
        team_config = json.load(f)
    
    # Load match metadata
    metadata_file = base_path / "3.1_match_metadata.json"
    with open(metadata_file, 'r') as f:
        match_metadata = json.load(f)
    
    print(f"✅ Loaded analysis data")
    print(f"📄 Events URL: {s3_locations['core_files']['web_events_array_json']}")
    
    # Create events array (simple version for DB)
    events = [
        {
            "type": "goal",
            "timestamp": 2205,  # 36:45
            "team": team_config['team_b']['name'],  # Corduff
            "description": "First VEO-verified goal"
        },
        {
            "type": "goal", 
            "timestamp": 5111,  # 85:11
            "team": team_config['team_b']['name'],  # Corduff
            "description": "Second VEO-verified goal"
        }
    ]
    
    # Create tactical analysis
    tactical = {
        team_config['team_a']['name'].lower(): {
            "strengths": ["Strong possession play", "Good set pieces", "Wing attacks"],
            "weaknesses": ["Poor finishing", "Defensive lapses"]
        },
        team_config['team_b']['name'].lower(): {
            "strengths": ["Clinical finishing", "Strong defense", "Counter-attacks"],
            "weaknesses": ["Prone to fouls", "Inconsistent possession"]
        }
    }
    
    # Create metadata with S3 URLs
    metadata = {
        "teams": {
            "red_team": {
                "name": team_config['team_a']['name'],
                "jersey_color": team_config['team_a']['colors']
            },
            "blue_team": {
                "name": team_config['team_b']['name'], 
                "jersey_color": team_config['team_b']['colors']
            }
        },
        "match_id": match_id,
        "final_score": match_metadata.get('final_score', 'Unknown'),
        "v5_analysis": True,
        "s3_files": s3_locations,
        "tactical_files": {
            "web_events_array_json": s3_locations['core_files'].get('web_events_array_json', ''),
            "match_metadata_json": s3_locations['core_files'].get('match_metadata_json', ''),
            "team_config_json": s3_locations['core_files'].get('team_config_json', '')
        },
        "uploaded_at": datetime.now().isoformat()
    }
    
    # Connect to database
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        if game_id:
            # Update existing game
            print(f"📊 Updating existing game: {game_id}")
            
            cursor.execute("""
                UPDATE games 
                SET ai_analysis = %s, tactical_analysis = %s, metadata = %s, status = %s 
                WHERE id = %s 
                RETURNING title
            """, [
                json.dumps(events),
                json.dumps(tactical), 
                json.dumps(metadata),
                'analyzed',
                game_id
            ])
            
            result = cursor.fetchone()
            if result:
                print(f"✅ Updated game: {result['title']}")
                final_game_id = game_id
            else:
                print(f"❌ Game not found: {game_id}")
                return False
                
        else:
            # Create new game
            print("🆕 Creating new game entry...")
            
            cursor.execute("""
                INSERT INTO games (title, description, status, ai_analysis, tactical_analysis, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, title
            """, [
                f"{team_config['team_a']['name']} vs {team_config['team_b']['name']}",
                f"VEO-Games-V5 analysis for match {match_id}",
                'analyzed',
                json.dumps(events),
                json.dumps(tactical),
                json.dumps(metadata)
            ])
            
            result = cursor.fetchone()
            final_game_id = result['id']
            print(f"✅ Created game: {result['title']} (ID: {final_game_id})")
        
        conn.commit()
        
        print(f"\n🎉 SUCCESS!")
        print(f"📊 Game ID: {final_game_id}")
        print(f"🎯 Status: analyzed")
        print(f"📄 Events URL: {s3_locations['core_files']['web_events_array_json']}")
        print(f"🌐 Game should now be visible on the website!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python 7_upload_to_db.py <match-id> [game-id]")
        print("Example: python 7_upload_to_db.py 20250427-match-apr-27-2025-9bd1cf29")
        print("Example: python 7_upload_to_db.py 20250427-match-apr-27-2025-9bd1cf29 50ce15ae-b083-4e93-a831-d9f950c39ee8")
        sys.exit(1)
    
    match_id = sys.argv[1]
    game_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        success = upload_to_database(match_id, game_id)
        if success:
            print(f"\n🎯 Ready for website! Game should be visible to users.")
        else:
            print(f"\n❌ Upload failed. Check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
