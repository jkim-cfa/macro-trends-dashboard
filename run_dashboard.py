import subprocess
import sys
import os

def main():
    try:
        # os.chdir("streamlit")  # Removed to keep working directory at project root
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit/Home.py",
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