#!/usr/bin/env python3
"""
Auto-commit script for maintaining GitHub contribution streak
Run this daily to keep your green graph going!
"""

import os
import subprocess
import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def auto_commit_project(project_path, commit_message=None):
    """Auto-commit changes in a project directory"""
    
    if not commit_message:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        commit_message = f"🤖 Daily auto-commit - {today}"
    
    print(f"Processing: {project_path}")
    
    # Check if it's a git repo
    is_git, _, _ = run_command("git status", cwd=project_path)
    if not is_git:
        print(f"❌ {project_path} is not a git repository")
        return False
    
    # Check for changes
    has_changes, stdout, _ = run_command("git status --porcelain", cwd=project_path)
    if not has_changes or not stdout.strip():
        print(f"✅ {project_path} - No changes to commit")
        return True
    
    # Add all changes
    success, _, error = run_command("git add .", cwd=project_path)
    if not success:
        print(f"❌ Failed to add changes in {project_path}: {error}")
        return False
    
    # Commit changes
    success, _, error = run_command(f'git commit -m "{commit_message}"', cwd=project_path)
    if not success:
        print(f"❌ Failed to commit in {project_path}: {error}")
        return False
    
    # Push changes
    success, _, error = run_command("git push origin main", cwd=project_path)
    if not success:
        # Try master branch
        success, _, error = run_command("git push origin master", cwd=project_path)
        if not success:
            print(f"❌ Failed to push in {project_path}: {error}")
            return False
    
    print(f"✅ Successfully committed and pushed: {project_path}")
    return True

def main():
    """Main function to process multiple projects"""
    
    # Add your project paths here
    projects = [
        "d:/campo",
        # Add more project paths:
        # "d:/project2", 
        # "d:/project3",
        # "d:/github/project4",
    ]
    
    print(f"🚀 Starting daily auto-commit - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_count = len(projects)
    
    for project_path in projects:
        if os.path.exists(project_path):
            if auto_commit_project(project_path):
                success_count += 1
        else:
            print(f"❌ Project path does not exist: {project_path}")
    
    print(f"\n📊 Summary: {success_count}/{total_count} projects processed successfully")
    
    if success_count == total_count:
        print("🎉 All projects committed! Your GitHub streak is safe! 🟢")
    else:
        print("⚠️ Some projects failed. Check the errors above.")

if __name__ == "__main__":
    main()
