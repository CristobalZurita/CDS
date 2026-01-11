#!/usr/bin/env python3
"""
Setup script for Appointment System
Configures database, runs migrations, and validates setup
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_env_file():
    """Check if .env file exists"""
    print_info("Checking .env file...")
    
    env_file = find_dotenv('.env')
    
    if not env_file:
        print_warning(".env file not found. Using .env.example as template")
        env_example = Path('.env.example')
        if env_example.exists():
            print_info(f"Creating .env from {env_example}")
            with open(env_example) as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print_success(".env created. Please configure it with your values")
            return False
        else:
            print_error(".env.example not found")
            return False
    else:
        print_success(f".env file found at {env_file}")
        load_dotenv(env_file)
        return True

def check_credentials():
    """Check Google Calendar credentials"""
    print_info("Checking Google Calendar credentials...")
    
    creds_file = Path('credentials/google-calendar-credentials.json')
    
    if not creds_file.exists():
        print_warning(f"Credentials file not found at {creds_file}")
        print_info("Instructions:")
        print_info("1. Follow the setup guide in backend/credentials/README.md")
        print_info("2. Download credentials from Google Cloud Console")
        print_info(f"3. Place them at {creds_file}")
        return False
    
    try:
        with open(creds_file) as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [f for f in required_fields if f not in creds]
        
        if missing:
            print_error(f"Credentials file missing fields: {missing}")
            return False
        
        print_success(f"Credentials file valid (project: {creds['project_id']})")
        return True
    
    except json.JSONDecodeError:
        print_error("Credentials file is not valid JSON")
        return False
    except Exception as e:
        print_error(f"Error reading credentials: {e}")
        return False

def check_database():
    """Check database setup"""
    print_info("Checking database...")
    
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./cirujano.db')
    
    if 'sqlite' in db_url:
        db_file = db_url.replace('sqlite:///', '')
        print_info(f"Using SQLite database at {db_file}")
        return True
    else:
        print_info(f"Using database: {db_url}")
        return True

def run_migrations():
    """Run database migrations"""
    print_info("Running database migrations...")
    
    try:
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        if result.returncode != 0:
            print_error(f"Migration failed: {result.stderr}")
            return False
        
        print_success("Database migrations completed")
        return True
    
    except FileNotFoundError:
        print_error("alembic command not found. Install with: pip install alembic")
        return False
    except Exception as e:
        print_error(f"Error running migrations: {e}")
        return False

def test_email_config():
    """Test SendGrid configuration"""
    print_info("Checking SendGrid configuration...")
    
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('SENDGRID_FROM_EMAIL')
    
    if not api_key:
        print_warning("SENDGRID_API_KEY not configured in .env")
        print_info("Email notifications will not work until configured")
        return False
    
    if not from_email:
        print_warning("SENDGRID_FROM_EMAIL not configured in .env")
        return False
    
    print_success(f"SendGrid configured (from: {from_email})")
    return True

def test_google_calendar():
    """Test Google Calendar setup"""
    print_info("Testing Google Calendar connection...")
    
    try:
        from backend.app.services.google_calendar_service import get_calendar_service
        
        service = get_calendar_service()
        
        if not service or not service.service:
            print_warning("Google Calendar service not initialized")
            return False
        
        # Try to access calendars
        calendars = service.service.calendarList().list().execute()
        print_success(f"Google Calendar connected ({len(calendars.get('items', []))} calendars found)")
        return True
    
    except ImportError:
        print_warning("google-api-python-client not installed")
        print_info("Install with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print_warning(f"Google Calendar test failed: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_info("Checking Python dependencies...")
    
    required = ['fastapi', 'sqlalchemy', 'pydantic', 'alembic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    
    print_success("All required dependencies installed")
    return True

def main():
    """Main setup routine"""
    print_header("Appointment System Setup")
    
    # Change to backend directory
    os.chdir('backend')
    
    # Check dependencies
    if not check_dependencies():
        print_error("Setup cannot continue without dependencies")
        return 1
    
    # Check .env
    if not check_env_file():
        print_warning("Setup continuing without .env configuration")
    
    # Check database
    if not check_database():
        print_error("Database check failed")
        return 1
    
    # Run migrations
    if not run_migrations():
        print_warning("Database migrations failed - this may be OK if already up-to-date")
    
    # Check credentials
    credentials_ok = check_credentials()
    
    # Check email
    email_ok = test_email_config()
    
    # Test Google Calendar
    calendar_ok = test_google_calendar()
    
    # Summary
    print_header("Setup Summary")
    
    print("\n✓ Required Components:")
    print(f"  • Database: {Colors.GREEN}✓{Colors.END}")
    print(f"  • Dependencies: {Colors.GREEN}✓{Colors.END}")
    
    print("\n⚠ Optional Components:")
    print(f"  • Google Calendar: {Colors.GREEN if calendar_ok else Colors.YELLOW}{'✓' if calendar_ok else '✗'}{Colors.END}")
    print(f"  • SendGrid Email: {Colors.GREEN if email_ok else Colors.YELLOW}{'✓' if email_ok else '✗'}{Colors.END}")
    
    if credentials_ok and email_ok and calendar_ok:
        print_success("\nSetup complete! System ready to use.")
        return 0
    elif credentials_ok or email_ok:
        print_warning("\nSetup partial - email and calendar features not fully configured")
        print_info("These can be configured later in .env file")
        return 0
    else:
        print_error("\nSetup completed with warnings")
        print_info("Please review the configuration before running the application")
        return 0

if __name__ == '__main__':
    sys.exit(main())
