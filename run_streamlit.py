#!/usr/bin/env python3
"""
Simple script to run the Streamlit application for the Enhanced Article Creator.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit application."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    app_path = project_root / "src" / "app.py"
    
    # Check if the app.py file exists
    if not app_path.exists():
        print(f"❌ Error: {app_path} not found!")
        print("Please make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    print("🚀 Starting Enhanced Article Creator Streamlit Application...")
    print(f"📁 App location: {app_path}")
    print("🌐 The application will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Run the Streamlit application using uv
        subprocess.run([
            "uv", "run", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
    except Exception as e:
        print(f"❌ Error running Streamlit application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 