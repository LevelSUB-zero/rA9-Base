#!/usr/bin/env python3
"""
RA9 Quick Setup Script

A simplified setup script for quick installation.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Quick setup for RA9."""
    print("RA9 Quick Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: Please run this script from the RA9 project root directory")
        return 1
    
    # Install in development mode
    try:
        print("Installing RA9 in development mode...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", ".[dev]"
        ], check=True)
        print("✓ Installation complete!")
        
        print("\nNext steps:")
        print("1. Copy env.example to .env and add your API keys")
        print("2. Run: python -m ra9.cli --help")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Installation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())