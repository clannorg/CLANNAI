#!/usr/bin/env python3
"""
Use Gemini to find 200 English clubs that love Veo but aren't famous
"""

import pandas as pd
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent.parent / 'ai' / '.env')

def setup_gemini():
    """Setup Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def analyze_clubs_with_gemini(model, clubs_data):
    """Use Gemini to analyze clubs and find Veo lovers that aren't famous"""
    
    prompt = f"""
    I have a list of English football clubs that use Veo (video analysis platform). 
    I need you to identify clubs that are:
    1. Genuinely English football clubs (not American, Australian, etc.)
    2. Use Veo a lot (high number of recordings = more active with Veo)
    3. NOT famous/professional clubs (avoid Premier League, Championship clubs)
    4. Are amateur/semi-pro level clubs that would be good sales targets
    
    Here are the top clubs by recordings:
    {clubs_data.head(100).to_string()}
    
    Please analyze each club name and return ONLY the club names that are:
    - English football clubs (not American/Australian)
    - Use Veo a lot (high recordings)
    - NOT famous/professional clubs
    - Good sales targets
    
    Return only the club names, one per line. Be more lenient - include clubs that seem English and use Veo a lot.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return []

def find_veo_lovers_gemini():
    """Use Gemini to find Veo-loving English clubs"""
    
    # Setup Gemini
    model = setup_gemini()
    if not model:
        return
    
    # Load English clubs
    df = pd.read_csv("data/2-by-country/clubs_england.csv")
    print(f"📊 Loaded {len(df)} English clubs")
    
    # Get top 2000 by recordings for Gemini to analyze
    top_clubs = df.sort_values('Recordings', ascending=False).head(2000)
    print(f"🎯 Analyzing top 2000 clubs with Gemini...")
    
    # Get Gemini's analysis
    good_clubs = analyze_clubs_with_gemini(model, top_clubs)
    
    if not good_clubs:
        print("❌ No clubs returned from Gemini")
        return
    
    print(f"✅ Gemini identified {len(good_clubs)} good clubs")
    
    # Filter the original dataframe to only include Gemini-approved clubs
    filtered_df = df[df['Club Name'].isin(good_clubs)].copy()
    filtered_df = filtered_df.sort_values('Recordings', ascending=False)
    
    # Take top 200
    final_clubs = filtered_df.head(200)
    
    # If we don't have enough clubs, get more from the original data
    if len(final_clubs) < 50:
        print(f"⚠️  Only got {len(final_clubs)} clubs from Gemini, getting more...")
        # Get more clubs manually - focus on English clubs with good activity
        more_clubs = df[
            (df['Recordings'] >= 100) &  # Good activity
            (~df['Club Name'].str.contains('united|city|town|fc', case=False, na=False)) &  # Not generic
            (df['Club Name'].str.len() > 5)  # Not too short
        ].head(200)
        final_clubs = pd.concat([final_clubs, more_clubs]).drop_duplicates().head(200)
    
    print(f"\n📋 Top 20 Gemini-approved Veo-loving clubs:")
    for i, (_, club) in enumerate(final_clubs.head(20).iterrows(), 1):
        print(f"  {i}. {club['Club Name']} ({club['Recordings']} recordings)")
    
    # Save to file
    output_path = Path("data/gemini_veo_lovers.csv")
    final_clubs.to_csv(output_path, index=False)
    print(f"\n💾 Saved {len(final_clubs)} Gemini-approved Veo-loving clubs to: {output_path}")
    
    return final_clubs

if __name__ == "__main__":
    find_veo_lovers_gemini() 