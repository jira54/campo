#!/usr/bin/env python
"""
Comprehensive database backup script for CampoPawa
Creates both SQL dump and JSON export of all data
"""
import os
import subprocess
import json
from datetime import datetime
from django.core.management import execute_from_command_line
from django.core.management.commands.dumpdata import Command as DumpDataCommand
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_sql_backup():
    """Create SQL dump using pg_dump"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"campo_backup_sql_{timestamp}.sql"
    
    try:
        # Extract connection details from DATABASE_URL
        # postgres://user:pass@host:port/dbname
        import re
        match = re.match(r'postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
        if match:
            user, password, host, port, dbname = match.groups()
            
            cmd = [
                'pg_dump',
                f'--host={host}',
                f'--port={port}',
                f'--username={user}',
                f'--dbname={dbname}',
                '--no-password',
                '--verbose',
                '--clean',
                '--no-acl',
                '--no-owner',
                f'--file={backup_file}'
            ]
            
            # Set password in environment
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            print(f"🔄 Creating SQL backup: {backup_file}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ SQL backup created: {backup_file}")
                return backup_file
            else:
                print(f"❌ SQL backup failed: {result.stderr}")
                return False
        else:
            print("❌ Could not parse DATABASE_URL")
            return False
            
    except Exception as e:
        print(f"❌ SQL backup error: {e}")
        return False

def create_json_backup():
    """Create JSON export of all Django data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"campo_backup_json_{timestamp}.json"
    
    try:
        print(f"🔄 Creating JSON backup: {backup_file}")
        
        # Export all data
        command = [
            'python', 'manage.py', 'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            f'--output={backup_file}'
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check file size
            file_size = os.path.getsize(backup_file)
            print(f"✅ JSON backup created: {backup_file} ({file_size:,} bytes)")
            return backup_file
        else:
            print(f"❌ JSON backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ JSON backup error: {e}")
        return False

def verify_backup(backup_file):
    """Verify backup file integrity"""
    try:
        if backup_file.endswith('.sql'):
            # Check if SQL file contains expected content
            with open(backup_file, 'r') as f:
                content = f.read()
                if 'CREATE TABLE' in content and 'INSERT INTO' in content:
                    print(f"✅ SQL backup verified: {len(content.splitlines())} lines")
                    return True
                else:
                    print("❌ SQL backup appears incomplete")
                    return False
                    
        elif backup_file.endswith('.json'):
            # Check if JSON file is valid
            with open(backup_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ JSON backup verified: {len(data)} records")
                    return True
                else:
                    print("❌ JSON backup appears empty or invalid")
                    return False
                    
    except Exception as e:
        print(f"❌ Backup verification error: {e}")
        return False

def main():
    print("🚀 Starting CampoPawa database backup...")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Create backups
    sql_backup = create_sql_backup()
    json_backup = create_json_backup()
    
    print("=" * 50)
    
    # Verify backups
    if sql_backup:
        verify_backup(sql_backup)
    if json_backup:
        verify_backup(json_backup)
    
    # Summary
    print("=" * 50)
    print("📋 BACKUP SUMMARY:")
    if sql_backup:
        print(f"✅ SQL: {sql_backup}")
    else:
        print("❌ SQL: Failed")
        
    if json_backup:
        print(f"✅ JSON: {json_backup}")
    else:
        print("❌ JSON: Failed")
    
    if sql_backup and json_backup:
        print("🎉 Both backups created successfully!")
        print("💾 Store these files safely before proceeding with app deletion.")
    else:
        print("⚠️  Some backups failed - review errors before proceeding.")

if __name__ == "__main__":
    main()
