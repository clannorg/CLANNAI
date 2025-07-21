#!/usr/bin/env python3
"""
Veo Video Downloader
Downloads football videos from Veo platform
"""

import os
import requests
import json
import subprocess
from pathlib import Path
import logging
from urllib.parse import urlparse, parse_qs
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoDownloader:
    """
    Downloads videos from Veo platform
    Handles authentication and video extraction
    """
    
    def __init__(self, output_dir: str = "0_utils/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        
        # Veo-specific headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_match_id(self, url: str) -> str | None:
        """
        Extract match ID from Veo URL
        """
        try:
            # Parse URL to get match ID
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            # Look for match ID pattern - it's usually after "matches/"
            for i, part in enumerate(path_parts):
                if part == "matches" and i + 1 < len(path_parts):
                    # The next part should be the match ID
                    match_id = path_parts[i + 1]
                    if match_id and match_id != "matches":
                        return match_id
            
            # Fallback: look for any part that looks like a match ID
            for part in path_parts:
                if part and part != "matches" and len(part) > 10:
                    return part
            
            return None
        except Exception as e:
            logger.error(f"Error extracting match ID: {e}")
            return None
    
    def extract_highlight_id(self, url: str) -> str | None:
        """
        Extract highlight ID from Veo URL
        """
        try:
            # Parse query parameters
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Look for highlight parameter
            if 'highlight' in query_params:
                return query_params['highlight'][0]
            
            return None
        except Exception as e:
            logger.error(f"Error extracting highlight ID: {e}")
            return None
    
    def get_video_url(self, match_id: str, highlight_id: str | None = None) -> str | None:
        """
        Get direct video URL from Veo API
        """
        try:
            # Construct API URL
            if highlight_id:
                api_url = f"https://app.veo.co/api/matches/{match_id}/highlights/{highlight_id}/video"
            else:
                api_url = f"https://app.veo.co/api/matches/{match_id}/video"
            
            logger.info(f"Requesting video URL from: {api_url}")
            
            response = self.session.get(api_url)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract video URL from response
            if 'video_url' in data:
                return data['video_url']
            elif 'url' in data:
                return data['url']
            else:
                logger.error(f"No video URL found in response: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting video URL: {e}")
            return None
    
    def download_video(self, url: str, filename: str | None = None) -> str | None:
        """
        Download video from Veo URL
        """
        try:
            # Extract IDs from URL
            match_id = self.extract_match_id(url)
            highlight_id = self.extract_highlight_id(url)
            
            if not match_id:
                logger.error("Could not extract match ID from URL")
                return None
            
            logger.info(f"Match ID: {match_id}")
            if highlight_id:
                logger.info(f"Highlight ID: {highlight_id}")
            
            # Get video URL
            video_url = self.get_video_url(match_id, highlight_id)
            if not video_url:
                logger.error("Could not get video URL")
                return None
            
            # Generate filename if not provided
            if not filename:
                if highlight_id:
                    filename = f"veo_highlight_{highlight_id}.mp4"
                else:
                    filename = f"veo_match_{match_id}.mp4"
            
            output_path = self.output_dir / filename
            
            logger.info(f"Downloading video to: {output_path}")
            
            # Download video with progress
            response = self.session.get(video_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 Downloading... {percent:.1f}%", end='', flush=True)
            
            print(f"\n✅ Download complete: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def download_with_yt_dlp(self, url: str, filename: str | None = None) -> str | None:
        """
        Alternative download method using yt-dlp
        """
        try:
            if not filename:
                filename = "veo_video.mp4"
            
            output_path = self.output_dir / filename
            
            # Use yt-dlp for more robust downloading
            cmd = [
                "yt-dlp",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--format", "best[ext=mp4]",
                "-o", str(output_path),
                url
            ]
            
            logger.info(f"Downloading with yt-dlp: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded: {output_path}")
                return str(output_path)
            else:
                logger.error(f"yt-dlp download failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error with yt-dlp download: {e}")
            return None

def main():
    """Test Veo downloader"""
    
    # Test URL
    url = "https://app.veo.co/matches/20250518-boys-academy-u16-vs-north-west-london-jets-1358e452/?highlight=c057a484-5e30-46cf-b295-00cc632a8e36&scroll=MT"
    
    downloader = VeoDownloader()
    
    print("🔍 Analyzing Veo URL...")
    match_id = downloader.extract_match_id(url)
    highlight_id = downloader.extract_highlight_id(url)
    
    print(f"Match ID: {match_id}")
    print(f"Highlight ID: {highlight_id}")
    
    print("\n📥 Attempting download...")
    
    # Try direct download first
    result = downloader.download_video(url)
    
    if not result:
        print("🔄 Trying yt-dlp method...")
        result = downloader.download_with_yt_dlp(url)
    
    if result:
        print(f"✅ Success! Video saved to: {result}")
    else:
        print("❌ Download failed. Veo may require authentication or the URL format has changed.")

if __name__ == "__main__":
    main() 