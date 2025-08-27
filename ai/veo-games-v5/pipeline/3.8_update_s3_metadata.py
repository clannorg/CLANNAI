#!/usr/bin/env python3
"""
Step 3.8: Update S3 Metadata
Updates the database metadata with S3 core locations to make training recommendations accessible.
"""

import json
import sys
import os
import psycopg2
from pathlib import Path
from datetime import datetime

def load_s3_core_locations(match_id):
    """Load S3 core locations"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    s3_file = base_path / "3.5_s3_core_locations.json"
    
    if not s3_file.exists():
        print(f"❌ S3 core locations not found: {s3_file}")
        return None
    
    with open(s3_file, 'r') as f:
        return json.load(f)

def load_website_game_id(match_id):
    """Load website game ID from file"""
    base_path = Path(__file__).parent.parent / "outputs" / match_id
    website_id_file = base_path / "website_game_id.txt"
    
    if not website_id_file.exists():
        print(f"❌ No website game ID found for: {match_id}")
        print(f"Run step 1.0 first: python 1.0_webid.py {match_id}")
        return None
    
    return website_id_file.read_text().strip()

def update_s3_metadata(match_id):
    """Update database metadata with S3 core locations"""
    print(f"🔗 Updating S3 metadata for: {match_id}")
    
    # Load S3 core locations
    s3_locations = load_s3_core_locations(match_id)
    if not s3_locations:
        return False
    
    # Load website game ID
    game_id = load_website_game_id(match_id)
    if not game_id:
        return False
    
    # Connect to database
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Get current metadata
        cur.execute("SELECT metadata FROM games WHERE id = %s", (game_id,))
        result = cur.fetchone()
        
        if not result:
            print(f"❌ Game not found: {game_id}")
            return False
        
        current_metadata = result[0] or {}
        
        # Update metadata with S3 files
        updated_metadata = {
            **current_metadata,
            "s3_files": s3_locations.get('core_files', {}),
            "s3_updated_at": datetime.now().isoformat()
        }
        
        # Update database
        cur.execute(
            "UPDATE games SET metadata = %s WHERE id = %s",
            (json.dumps(updated_metadata), game_id)
        )
        
        conn.commit()
        
        print(f"✅ S3 metadata updated for game: {game_id}")
        print(f"📦 Added {len(s3_locations.get('core_files', {}))} S3 file URLs")
        
        # Show training recommendations URL if available
        training_url = s3_locations.get('core_files', {}).get('training_recommendations_json')
        if training_url:
            print(f"🏋️ Training recommendations URL: {training_url}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 3.8_update_s3_metadata.py <match-id>")
        print("Example: python 3.8_update_s3_metadata.py 20250427-match-apr-27-2025-9bd1cf29")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    success = update_s3_metadata(match_id)
    if not success:
        sys.exit(1)
    
    print("\n🎯 S3 metadata update complete!")
    print("Training recommendations should now be accessible on the website.")

if __name__ == "__main__":
    main()
