#!/usr/bin/env python3
"""
Cross-platform startup script for NewsPulse Backend
Handles both Windows and Unix-like systems
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_python_executable():
    """Get the appropriate Python executable for the current platform"""
    if platform.system() == "Windows":
        return "python"
    else:
        return "python3"

def get_venv_activation_command():
    """Get the virtual environment activation command for the current platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def check_venv():
    """Check if virtual environment exists"""
    if platform.system() == "Windows":
        venv_path = Path("venv/Scripts/python.exe")
    else:
        venv_path = Path("venv/bin/python")
    
    return venv_path.exists()

def create_venv():
    """Create virtual environment"""
    python_cmd = get_python_executable()
    print(f"Creating virtual environment using {python_cmd}...")
    
    try:
        subprocess.run([python_cmd, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install requirements using the virtual environment Python"""
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    print("Installing requirements...")
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_server():
    """Run the FastAPI server"""
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    print("Starting NewsPulse API server...")
    print("🚀 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([python_cmd, "run_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main startup function"""
    print("🚀 NewsPulse Backend Startup Script")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print("-" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    if not check_venv():
        print("📦 Virtual environment not found. Creating...")
        if not create_venv():
            sys.exit(1)
    else:
        print("✅ Virtual environment found!")
    
    # Install/update requirements
    if not install_requirements():
        sys.exit(1)
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main()