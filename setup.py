#!/usr/bin/env python3
"""
Setup script to initialize or reset the database.
Run this any time you want to reset the DB and seed an admin user.
It does NOT delete any files.
"""

import os
import sys

def main():
    """Run database setup (with optional reset)"""
    print("Setting up database...")
    
    # Import and run database initialization
    try:
        from database import create_app, init_db

        reset = '--reset' in sys.argv
        app = create_app()
        init_db(app, reset=reset)

        print("\n" + "="*50)
        print("SETUP COMPLETE!")
        print("="*50)
        print("Database is ready with admin user:")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("\nRun the Flask app: python app.py")
        if reset:
            print("(Database was dropped and recreated due to --reset)")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
