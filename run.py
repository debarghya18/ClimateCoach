#!/usr/bin/env python3
"""
ClimateCoach Launcher
Simple script to run the ClimateCoach application
"""

import subprocess
import sys
import os

def main():
    """Launch the ClimateCoach application"""
    print("🌍 Starting ClimateCoach...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this from the climate-ai-platform directory.")
        return
    
    try:
        # Run the application
        print("🚀 Launching ClimateCoach application...")
        print("📱 The app will open in your browser at: http://localhost:8501")
        print("⏳ Please wait...")
        
        # Run streamlit with the main.py file
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 ClimateCoach stopped by user")
    except Exception as e:
        print(f"❌ Error starting ClimateCoach: {e}")
        print("💡 Make sure you have all dependencies installed:")
        print("   pip install streamlit plotly pandas numpy")

if __name__ == "__main__":
    main() 