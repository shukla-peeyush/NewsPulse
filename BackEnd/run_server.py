"""
Script to run the NewsPulse API server
"""

import sys
import os
import socket

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
from src.api.main_simple import app

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False

if __name__ == "__main__":
    print("Starting NewsPulse API server...")
    print("🔍 Looking for available port...")
    print("📋 Will try ports: 8000, 8001, 8002, 8003")
    
    # Try different ports if 8000 is in use
    ports_to_try = [8000, 8001, 8002, 8003]
    available_port = None
    
    # Find first available port
    for port in ports_to_try:
        print(f"🔍 Checking port {port}...")
        if is_port_available(port):
            available_port = port
            print(f"✅ Port {port} is available!")
            break
        else:
            print(f"❌ Port {port} is already in use")
    
    if available_port is None:
        print("\n❌ All ports (8000-8003) are in use!")
        print("💡 Please stop other services or kill existing processes:")
        print("   lsof -i :8000")
        print("   kill -9 <PID>")
        print("   Or use: pkill -f 'python.*8000'")
        sys.exit(1)
    
    print(f"\n🚀 Starting server on port {available_port}...")
    print(f"📍 API will be available at: http://localhost:{available_port}")
    print(f"📚 API Documentation: http://localhost:{available_port}/docs")
    print(f"❤️  Health Check: http://localhost:{available_port}/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=available_port, 
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")