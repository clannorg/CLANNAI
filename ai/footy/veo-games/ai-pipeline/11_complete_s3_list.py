#!/usr/bin/env python3
"""
Generate complete S3 files list from s3_locations.json
"""

import json
import sys
from pathlib import Path

def generate_complete_s3_list(match_id):
    """Generate complete S3 files list from JSON"""
    
    data_dir = Path("../data") / match_id
    s3_json_path = data_dir / "s3_locations.json"
    output_path = data_dir / "complete_s3_files.txt"
    
    if not s3_json_path.exists():
        print(f"❌ S3 locations file not found: {s3_json_path}")
        return False
    
    print(f"📋 Generating complete S3 files list for {match_id}")
    
    # Read S3 locations JSON
    with open(s3_json_path, 'r') as f:
        s3_data = json.load(f)
    
    # Generate the complete files list
    lines = [
        f"# Complete S3 Analysis Files - {match_id}",
        "# All files uploaded and ready for web app",
        ""
    ]
    
    # Add main video first if it exists
    s3_urls = s3_data.get("s3_urls", {})
    if "video.mp4" in s3_urls:
        video = s3_urls["video.mp4"]
        lines.extend([
            "# MAIN VIDEO",
            f"video.mp4={video['url']} ({video['file_size_mb']}MB)",
            ""
        ])
    
    # Add web app data
    web_files = [k for k in s3_urls.keys() if k.startswith("web_events")]
    if web_files:
        lines.append("# WEB APP DATA")
        for filename in sorted(web_files):
            file_data = s3_urls[filename]
            lines.append(f"{filename}={file_data['url']} ({file_data['file_size_mb']}MB)")
        lines.append("")
    
    # Add analysis reports
    analysis_files = [k for k in s3_urls.keys() if k.endswith('.txt') and not k.startswith('web_')]
    if analysis_files:
        lines.append("# ANALYSIS REPORTS")
        for filename in sorted(analysis_files):
            file_data = s3_urls[filename]
            lines.append(f"{filename}={file_data['url']} ({file_data['file_size_mb']}MB)")
        lines.append("")
    
    # Add ground truth data
    json_files = [k for k in s3_urls.keys() if k.endswith('.json') and not k.startswith('web_')]
    if json_files:
        lines.append("# GROUND TRUTH DATA")
        for filename in sorted(json_files):
            file_data = s3_urls[filename]
            lines.append(f"{filename}={file_data['url']} ({file_data['file_size_mb']}MB)")
        lines.append("")
    
    # Add summary
    summary = s3_data.get("upload_summary", {})
    total_files = summary.get("total_files", "?")
    successful = summary.get("successful_uploads", "?")
    total_size = summary.get("total_size_mb", "?")
    
    lines.extend([
        f"# SUMMARY: {successful}/{total_files} files uploaded successfully ({total_size}MB total)",
        "# Ready for ClannAI web app integration!"
    ])
    
    # Write the complete file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Complete S3 files list saved to: {output_path}")
    print(f"📊 {successful}/{total_files} files ({total_size}MB total)")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 11_complete_s3_list.py <match-id>")
        print("Example: python 11_complete_s3_list.py newmills-20250222")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = generate_complete_s3_list(match_id)
    
    if success:
        print(f"🎉 Complete S3 list generated for {match_id}")
    else:
        print(f"❌ Failed to generate S3 list for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()