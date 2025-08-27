#!/usr/bin/env python3
"""
Step 1.0: Link pipeline to website game
Queries database games and lets user select which one they're analyzing.
Creates website_game_id.txt mapping file.
"""

import json
import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

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
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def get_games_list():
    """Get list of games from database"""
    conn = connect_to_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, status, created_at 
            FROM games 
            ORDER BY created_at DESC 
            LIMIT 20
        """)
        
        games = cursor.fetchall()
        return games
        
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return []
    finally:
        conn.close()

def display_games(games):
    """Display games with numbered list"""
    print("\n🎮 Available games on website:")
    print("=" * 80)
    
    for i, game in enumerate(games, 1):
        status_emoji = "✅" if game['status'] == 'analyzed' else "⏳"
        created = game['created_at'].strftime("%Y-%m-%d")
        
        print(f"{i:2d}. {status_emoji} {game['title']}")
        print(f"    ID: {game['id']}")
        print(f"    Created: {created}")
        print("-" * 40)
    
    print(f"\n📋 Total: {len(games)} games")

def get_user_selection(games):
    """Get user's game selection"""
    while True:
        try:
            choice = input(f"\n🎯 Select game (1-{len(games)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(games):
                return games[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(games)}")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return None

def save_website_game_id(match_id, game_id, game_title):
    """Save website game ID to output folder"""
    output_dir = Path(__file__).parent.parent / "outputs" / match_id
    
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        print("Run step 1.1 first to create the match directory")
        return False
    
    # Save game ID
    id_file = output_dir / "website_game_id.txt"
    id_file.write_text(game_id)
    
    # Save game info for reference
    info_file = output_dir / "1.0_website_link.json"
    info = {
        "website_game_id": game_id,
        "website_game_title": game_title,
        "pipeline_match_id": match_id,
        "linked_at": "2025-08-27T16:30:00Z"
    }
    info_file.write_text(json.dumps(info, indent=2))
    
    print(f"✅ Website game ID saved: {id_file}")
    print(f"📄 Link info saved: {info_file}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python 1.0_webid.py <match-id>")
        print("Example: python 1.0_webid.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    print(f"🔗 Linking pipeline match '{match_id}' to website game...")
    
    # Get games from database
    games = get_games_list()
    if not games:
        print("❌ No games found in database")
        sys.exit(1)
    
    # Display games and get selection
    display_games(games)
    selected_game = get_user_selection(games)
    
    if not selected_game:
        print("👋 No game selected. Exiting.")
        sys.exit(0)
    
    # Save the mapping
    success = save_website_game_id(
        match_id, 
        selected_game['id'], 
        selected_game['title']
    )
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"🔗 Pipeline match: {match_id}")
        print(f"🌐 Website game: {selected_game['title']}")
        print(f"📋 Game ID: {selected_game['id']}")
        print(f"\n🎯 Now run your analysis pipeline - it will auto-update this game!")
    else:
        print(f"\n❌ Failed to save website game ID")
        sys.exit(1)

if __name__ == "__main__":
    main()
