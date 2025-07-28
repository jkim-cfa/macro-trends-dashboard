#!/usr/bin/env python3
"""
Global Event Dashboard Launcher
Run this script to start the unified dashboard with agriculture and defence sectors.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    try:
        # Change to the streamlit directory
        os.chdir("streamlit")
        
        # Run the home dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error running dashboard: {e}")
        print("Make sure you have streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main() 