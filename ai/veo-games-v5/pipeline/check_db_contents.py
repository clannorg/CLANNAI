#!/usr/bin/env python3
"""
Check what's actually in the database for any game
Usage: python check_db_contents.py <game-id>
"""

import json
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

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

def check_game_data(game_id):
    """Check what's actually in the database for a specific game"""
    database_url = load_env_vars()
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    print(f"🔍 Checking database contents for game: {game_id}")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            sslmode='require' if 'rds.amazonaws.com' in database_url else 'disable'
        )
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT title, status, 
                   CASE WHEN ai_analysis IS NOT NULL THEN 'YES' ELSE 'NO' END as has_ai_analysis,
                   CASE WHEN tactical_analysis IS NOT NULL THEN 'YES' ELSE 'NO' END as has_tactical,
                   CASE WHEN metadata IS NOT NULL THEN 'YES' ELSE 'NO' END as has_metadata,
                   video_url, s3_key
            FROM games 
            WHERE id = %s
        """, [game_id])
        
        result = cursor.fetchone()
        
        if result:
            print(f"🎮 Game: {result['title']}")
            print(f"🎯 Status: {result['status']}")
            print(f"🤖 AI Analysis: {result['has_ai_analysis']}")
            print(f"📊 Tactical: {result['has_tactical']}")
            print(f"📋 Metadata: {result['has_metadata']}")
            print(f"🎬 Video URL: {result['video_url'] or 'None'}")
            print(f"📦 S3 Key: {result['s3_key'] or 'None'}")
            
            # Check metadata contents
            cursor.execute("SELECT metadata FROM games WHERE id = %s", [game_id])
            metadata_result = cursor.fetchone()
            
            if metadata_result and metadata_result['metadata']:
                metadata = metadata_result['metadata']
                print(f"\n📋 METADATA CONTENTS:")
                
                if 's3_files' in metadata:
                    print(f"\n📦 S3_FILES:")
                    s3_files = metadata['s3_files']
                    for file_name, file_info in s3_files.items():
                        url = file_info.get('url', 'No URL')
                        print(f"   📄 {file_name}")
                        print(f"      URL: {url}")
                        print(f"      Description: {file_info.get('description', 'N/A')}")
                        print()
                else:
                    print(f"❌ No s3_files in metadata")
                
                if 'tactical_files' in metadata:
                    print(f"🎯 TACTICAL_FILES:")
                    tactical_files = metadata['tactical_files']
                    for file_name, url in tactical_files.items():
                        print(f"   🎯 {file_name}")
                        print(f"      URL: {url}")
                        print()
                else:
                    print(f"❌ No tactical_files in metadata")
                    
                # Show team info if available
                if 'teams' in metadata:
                    print(f"👕 TEAM INFO:")
                    teams = metadata['teams']
                    for team_key, team_info in teams.items():
                        print(f"   {team_key}: {team_info.get('name', 'Unknown')} ({team_info.get('jersey_color', 'Unknown colors')})")
                    print()
                
                # Show match info
                if 'match_id' in metadata:
                    print(f"🎮 MATCH INFO:")
                    print(f"   Match ID: {metadata.get('match_id', 'N/A')}")
                    print(f"   Final Score: {metadata.get('final_score', 'N/A')}")
                    print(f"   V5 Analysis: {metadata.get('v5_analysis', 'N/A')}")
                    print(f"   Uploaded: {metadata.get('uploaded_at', 'N/A')}")
                    print()
            else:
                print(f"❌ No metadata found")
                
        else:
            print(f"❌ Game not found: {game_id}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

def list_games_by_title(search_term=None):
    """List games in database, optionally filtered by title"""
    database_url = load_env_vars()
    if not database_url:
        print("❌ DATABASE_URL not found")
        return
    
    try:
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor,
            sslmode='require' if 'rds.amazonaws.com' in database_url else 'disable'
        )
        
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute("""
                SELECT id, title, status, created_at
                FROM games 
                WHERE title ILIKE %s
                ORDER BY created_at DESC
                LIMIT 10
            """, [f'%{search_term}%'])
            print(f"🔍 Games matching '{search_term}':")
        else:
            cursor.execute("""
                SELECT id, title, status, created_at
                FROM games 
                ORDER BY created_at DESC
                LIMIT 10
            """)
            print(f"🎮 Recent games:")
        
        results = cursor.fetchall()
        
        if results:
            print("=" * 80)
            for game in results:
                print(f"ID: {game['id']}")
                print(f"Title: {game['title']}")
                print(f"Status: {game['status']}")
                print(f"Created: {game['created_at']}")
                print("-" * 40)
        else:
            print("No games found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_db_contents.py <game-id>           # Check specific game")
        print("  python check_db_contents.py --list [search]     # List games")
        print()
        print("Examples:")
        print("  python check_db_contents.py 50ce15ae-b083-4e93-a831-d9f950c39ee8")
        print("  python check_db_contents.py --list dalkey")
        print("  python check_db_contents.py --list")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        search_term = sys.argv[2] if len(sys.argv) > 2 else None
        list_games_by_title(search_term)
    else:
        game_id = sys.argv[1]
        check_game_data(game_id)
