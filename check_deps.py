#!/usr/bin/env python3
"""
RA9 Dependency Checker
Simple script to verify all required dependencies are installed.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependency(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Missing")
        return False

def install_missing_deps(missing_deps):
    """Install missing dependencies."""
    if not missing_deps:
        return True
    
    print(f"\n🔧 Installing missing dependencies: {', '.join(missing_deps)}")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade"
        ] + missing_deps, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main function."""
    print("🔍 RA9 Dependency Checker")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check core dependencies
    print("\n📦 Checking core dependencies:")
    dependencies = [
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("typer", "typer"),
        ("structlog", "structlog"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("langchain", "langchain"),
        ("python-dotenv", "dotenv"),
    ]
    
    missing = []
    for package, import_name in dependencies:
        if not check_dependency(package, import_name):
            missing.append(package)
    
    # Check RA9 package
    print("\n🏗️ Checking RA9 package:")
    try:
        import ra9
        print("✅ ra9 package")
    except ImportError:
        print("❌ ra9 package - Not installed")
        missing.append("ra9 (run: pip install -e .)")
    
    # Summary
    print("\n📊 Summary:")
    if missing:
        print(f"❌ {len(missing)} missing dependencies")
        print("\n🔧 To fix:")
        if "ra9 (run: pip install -e .)" in missing:
            print("1. Install RA9 package: pip install -e .")
            missing.remove("ra9 (run: pip install -e .)")
        
        if missing:
            print(f"2. Install missing dependencies: pip install {' '.join(missing)}")
        
        print("\n💡 Or use the automated installer:")
        print("   python install_current.py")
        
        return 1
    else:
        print("✅ All dependencies are installed!")
        print("\n🚀 You can now run RA9:")
        print("   python -m ra9.cli process --query 'Hello!'")
        return 0

if __name__ == "__main__":
    sys.exit(main())
