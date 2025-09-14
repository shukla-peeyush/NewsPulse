#!/usr/bin/env python3
"""
Simple test script to verify the setup works
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if we can import the required modules"""
    print("🧪 Testing imports...")
    
    # Add src to path
    script_dir = Path(__file__).parent
    src_path = script_dir / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        print("📦 Testing transformers...")
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        
        print("📦 Testing torch...")
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        print("📦 Testing database modules...")
        from storage.database import get_db_session, test_connection
        from storage.models_simple import Article, NewsSource
        print("✅ Database modules imported successfully")
        
        print("📦 Testing database connection...")
        if test_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 NewsPulse Setup Test")
    print("=" * 40)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if we're in the right place
    src_dir = current_dir / "src"
    if not src_dir.exists():
        print("❌ 'src' directory not found!")
        print("💡 Make sure you're in the BackEnd directory")
        print("💡 Try: cd /Users/peeyush.shukla/Desktop/NewsPulse/BackEnd")
        return False
    
    print(f"✅ Found src directory: {src_dir}")
    
    # Test imports
    if test_imports():
        print("\n🎉 All tests passed! Your setup is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)