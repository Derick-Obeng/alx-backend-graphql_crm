#!/usr/bin/env python
"""
Setup script for the Django CRM GraphQL project with cron jobs.
This script will install dependencies, run migrations, and set up cron jobs.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    print("Django CRM GraphQL Setup Script")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"Working directory: {project_dir}")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Failed to install dependencies. Please install manually.")
        return False
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Making migrations"):
        print("Failed to make migrations.")
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("Failed to run migrations.")
        return False
    
    # Create superuser (optional)
    print("\nCreating superuser (optional)...")
    print("You can skip this by pressing Ctrl+C")
    try:
        subprocess.run("python manage.py createsuperuser", shell=True, check=True)
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print("Skipped superuser creation.")
    
    # Add cron jobs
    if not run_command("python manage.py crontab add", "Adding cron jobs"):
        print("Failed to add cron jobs. You may need to add them manually.")
    
    # Show cron jobs
    run_command("python manage.py crontab show", "Showing current cron jobs")
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("=" * 50)
    
    print("\nTo test the setup:")
    print("1. Run the development server: python manage.py runserver")
    print("2. Visit http://localhost:8000/graphql/ to test GraphQL mutations")
    print("3. Run the test script: python test_low_stock_update.py")
    
    print("\nTo manage cron jobs:")
    print("- View current jobs: python manage.py crontab show")
    print("- Remove all jobs: python manage.py crontab remove")
    print("- Add jobs: python manage.py crontab add")
    
    print("\nThe cron job will run every 12 hours to update low-stock products.")
    print("Logs will be written to /tmp/low_stock_updates_log.txt")


if __name__ == "__main__":
    main()
