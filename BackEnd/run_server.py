"""
Script to run the NewsPulse API server
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
from src.api.main_simple import app

if __name__ == "__main__":
    print("Starting NewsPulse API server...")
    print("🔍 Looking for available port...")
    print("📋 Will try ports: 8000, 8001, 8002, 8003")
    
    # Try different ports if 8000 is in use
    ports_to_try = [8000, 8001, 8002, 8003]
    
    for port in ports_to_try:
        try:
            print(f"Trying to start server on port {port}...")
            print(f"🚀 API will be available at: http://localhost:{port}")
            print(f"📚 API Documentation: http://localhost:{port}/docs")
            print(f"❤️  Health Check: http://localhost:{port}/health")
            print("\nPress Ctrl+C to stop the server\n")
            
            uvicorn.run(
                app, 
                host="127.0.0.1", 
                port=port, 
                log_level="info",
                reload=False
            )
            break
        except OSError as e:
            if "Address already in use" in str(e) or "error while attempting to bind" in str(e):
                print(f"Port {port} is already in use, trying next port...")
                if port == ports_to_try[-1]:
                    print("❌ All ports are in use. Please stop other services or use a different port.")
                    print("💡 You can kill existing processes with: lsof -i :8000 && kill -9 <PID>")
                continue
            else:
                raise e