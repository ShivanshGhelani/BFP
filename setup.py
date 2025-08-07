#!/usr/bin/env python3
"""
Setup script for BFP (Browser Fingerprinting Platform)
This script installs the required dependencies and sets up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up BFP (Browser Fingerprinting Platform)")
    print("=" * 60)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You are not in a virtual environment!")
        print("It's recommended to create and activate a virtual environment first:")
        print("   python -m venv bfp")
        print("   bfp\\Scripts\\activate  # On Windows")
        print("   source bfp/bin/activate  # On Linux/Mac")
        
        choice = input("\n🤔 Do you want to continue anyway? (y/N): ").lower()
        if choice != 'y':
            print("Setup cancelled. Please activate your virtual environment and run this script again.")
            return False
    
    # Install dependencies
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Check if Redis is installed (optional)
    print("\n" + "="*50)
    print("🔍 Checking Redis installation")
    print("="*50)
    
    try:
        subprocess.run("redis-server --version", shell=True, check=True, capture_output=True)
        print("✅ Redis is installed and available")
    except subprocess.CalledProcessError:
        print("⚠️  Redis is not installed or not in PATH")
        print("Redis is optional but recommended for caching geolocation data.")
        print("Install Redis:")
        print("  - Windows: Download from https://redis.io/download")
        print("  - Ubuntu/Debian: sudo apt-get install redis-server")
        print("  - macOS: brew install redis")
        print("  - Or use Docker: docker run -d -p 6379:6379 redis:alpine")
    
    # Check environment file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n" + "="*50)
        print("⚠️  .env file not found")
        print("="*50)
        print("Please create a .env file with the required configuration.")
        print("You can copy from .env.example if available.")
        return False
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Make sure MongoDB is running and accessible")
    print("2. Start Redis server (optional but recommended):")
    print("   redis-server")
    print("3. Run the application:")
    print("   python main.py")
    print("   or")
    print("   uvicorn main:app --reload")
    print("\n🌐 The API will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
