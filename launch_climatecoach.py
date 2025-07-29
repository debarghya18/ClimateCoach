#!/usr/bin/env python3
"""
Launch script for ClimateCoach Streamlit UI
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the ClimateCoach Streamlit UI"""
    print("🌍 Starting ClimateCoach - AI Behavioral Nudging Platform...")
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Path to the Streamlit app
    app_path = script_dir / "src" / "ui" / "streamlit_app.py"
    
    # Check if the app file exists
    if not app_path.exists():
        print(f"❌ Error: Streamlit app not found at {app_path}")
        print("🔧 Creating the app structure...")
        # We'll create the structure if it doesn't exist
        create_app_structure(script_dir)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = str(script_dir)
    
    try:
        # Launch Streamlit
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(app_path),
            "--server.port=8502",
            "--server.address=localhost",
            "--theme.base=light",
            "--theme.primaryColor=#2E8B57",
            "--theme.backgroundColor=#f0f8f0",
            "--theme.secondaryBackgroundColor=#ffffff",
            "--theme.textColor=#2c3e50"
        ]
        
        print(f"🚀 Launching ClimateCoach UI...")
        print(f"📍 URL: http://localhost:8502")
        print(f"💡 Press Ctrl+C to stop the server")
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping ClimateCoach UI...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def create_app_structure(base_dir):
    """Create the basic app structure if it doesn't exist"""
    directories = [
        "src/ui",
        "src/agents",
        "src/services",
        "src/models",
        "src/utils",
        "data",
        "config",
        "tests"
    ]
    
    for directory in directories:
        (base_dir / directory).mkdir(parents=True, exist_ok=True)
        
    print("✅ Created basic app structure")

if __name__ == "__main__":
    main()
