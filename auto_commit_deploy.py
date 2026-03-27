import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🚀 CampoPawa Auto-Commit & Deploy Script")
    print("=" * 50)
    
    # Change to project directory
    os.chdir('d:\\campo')
    
    # Commands to run
    commands = [
        ('git add .', 'Stage all changes'),
        ('git commit -m "Auto-commit: Analytics fixes and enhanced data"', 'Commit changes to GitHub'),
        ('git push origin main', 'Push to GitHub'),
        ('fly deploy', 'Deploy to Fly.io'),
    ]
    
    success_count = 0
    
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n⚠️  Stopping due to failure in: {description}")
            break
    
    print(f"\n📊 Summary: {success_count}/{len(commands)} commands successful")
    
    if success_count == len(commands):
        print("🎉 All operations completed successfully!")
        print("📱 Your app is updated and deployed")
        print("💻 GitHub is synced with green commit")
        print("🌐 App is running at: https://campo.fly.dev")
    else:
        print("⚠️  Some operations failed. Check the errors above.")
    
    # Keep window open
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
