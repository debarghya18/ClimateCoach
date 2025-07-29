#!/usr/bin/env python3
"""
ClimateCoach Setup Script
Quick setup for the ClimateCoach carbon footprint reduction platform
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🌍 ClimateCoach Setup                     ║
    ║                                                              ║
    ║  AI-Powered Carbon Footprint Reduction Platform              ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • User Authentication & Profiles                            ║
    ║  • Real-time Carbon Footprint Tracking                       ║
    ║  • AI-Powered Recommendations                                ║
    ║  • Community Features & Challenges                           ║
    ║  • Gamification & Achievements                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install simple requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_simple.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_database():
    """Initialize the database with sample data"""
    print("\n🗄️ Setting up database...")
    
    try:
        # Import and initialize auth service
        sys.path.append('src')
        from core.auth import UserAuth
        
        auth = UserAuth()
        print("✅ Database initialized")
        
        # Add sample users for testing
        sample_users = [
            {
                "username": "demo_user",
                "email": "demo@climatecoach.com",
                "password": "demo123",
                "full_name": "Demo User",
                "location": "New York",
                "diet_preference": "vegetarian",
                "transport_preference": "bike",
                "household_size": 2
            },
            {
                "username": "eco_warrior",
                "email": "eco@climatecoach.com", 
                "password": "eco123",
                "full_name": "Eco Warrior",
                "location": "San Francisco",
                "diet_preference": "vegan",
                "transport_preference": "walk",
                "household_size": 1
            }
        ]
        
        for user in sample_users:
            try:
                auth.register_user(**user)
                print(f"✅ Created sample user: {user['username']}")
            except:
                print(f"ℹ️ User {user['username']} already exists")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n⚙️ Setting up environment variables...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                env_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created .env file from template")
        else:
            # Create basic .env file
            env_content = """# ClimateCoach Environment Variables

# Database
DATABASE_URL=sqlite:///climatecoach.db

# Optional: OpenAI API Key (for enhanced AI features)
# OPENAI_API_KEY=your_openai_api_key_here

# Optional: Weather API Key
# METEOSTAT_API_KEY=your_meteostat_api_key_here

# Optional: AWS S3 (for file storage)
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key
# AWS_S3_BUCKET=your_s3_bucket_name

# Optional: Monitoring
PROMETHEUS_ENABLED=false
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created basic .env file")
    else:
        print("ℹ️ .env file already exists")

def run_tests():
    """Run basic tests to ensure everything works"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test database connection
        conn = sqlite3.connect("climatecoach.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        expected_tables = ['users', 'daily_activities', 'carbon_footprints', 'community_posts']
        found_tables = [table[0] for table in tables]
        
        missing_tables = set(expected_tables) - set(found_tables)
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        
        print("✅ Database tables verified")
        print("✅ Basic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("""
    🎉 Setup Complete!
    
    Next Steps:
    
    1. Start the application:
       streamlit run app.py
    
    2. Open your browser and go to:
       http://localhost:8501
    
    3. Login with sample credentials:
       Username: demo_user
       Password: demo123
    
    4. Explore the features:
       • Log your daily activities
       • View your carbon footprint
       • Get AI recommendations
       • Join community discussions
       • Participate in challenges
    
    5. Optional: Configure API keys in .env file for enhanced features
    
    For Docker deployment:
    docker-compose up --build
    
    Documentation: README.md
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed at database setup")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Run tests
    if not run_tests():
        print("❌ Setup failed at testing")
        sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    main() 