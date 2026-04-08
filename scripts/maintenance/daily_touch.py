#!/usr/bin/env python3
"""
Simple daily touch script for GitHub contribution streak
Just updates a file to maintain daily activity
"""

import os
import subprocess
import datetime
from pathlib import Path

def daily_commit():
    """Simple daily commit to maintain streak"""
    
    # Create/update a daily activity file
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    activity_file = Path("daily_activity.md")
    
    # Append today's activity
    with open(activity_file, "a", encoding="utf-8") as f:
        f.write(f"\n## {today}\n")
        f.write(f"- 🤖 Auto-commit activity at {datetime.datetime.now().strftime('%H:%M:%S')}\n")
        f.write(f"- Maintaining GitHub contribution streak 🟢\n")
    
    # Git commands
    commands = [
        "git add daily_activity.md",
        f"git commit -m '🟢 Daily activity - {today}'",
        "git push origin main || git push origin master"
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Command failed: {cmd}")
                print(f"Error: {result.stderr}")
            else:
                print(f"✅ Success: {cmd}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"🎉 Daily activity committed for {today}!")

if __name__ == "__main__":
    daily_commit()
