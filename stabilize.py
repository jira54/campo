import os
import sys
import subprocess

def run_cmd(cmd):
    print(f"🚀 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    else:
        print(f"✅ Success: {result.stdout}")
    return result.returncode

def main():
    print("🛠️ Starting Post-Repair Stabilization...")
    
    # 1. Fake the migration that removes the already-deleted tables
    # This prevents the 'relation does not exist' error
    run_cmd("python manage.py migrate --fake vendors 0010")
    
    # 2. Run standard migrate for anything else
    ret = run_cmd("python manage.py migrate")
    
    if ret == 0:
        print("🎉 Stabilization Complete!")
    else:
        print("⚠️ Migration finished with issues, but core fake was attempted.")
        sys.exit(ret)

if __name__ == "__main__":
    main()
