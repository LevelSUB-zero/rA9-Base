#!/usr/bin/env python3
"""
RA9 Current Branch - Quick Install Script

This script provides a streamlined installation for the Current branch.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_step(message):
    """Print step message."""
    print(f"\n🔧 {message}")


def print_success(message):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message):
    """Print error message."""
    print(f"❌ {message}")


def print_warning(message):
    """Print warning message."""
    print(f"⚠️  {message}")


def main():
    """Main installation function."""
    print("🚀 RA9 Current Branch - Quick Install")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ required")
        return 1
    
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    print_step("Creating virtual environment...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_warning("Virtual environment already exists")
    else:
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print_success("Virtual environment created")
        except subprocess.CalledProcessError:
            print_error("Failed to create virtual environment")
            return 1
    
    # Get pip command
    if platform.system().lower() == "windows":
        pip_cmd = [str(venv_path / "Scripts" / "pip.exe")]
        python_cmd = [str(venv_path / "Scripts" / "python.exe")]
    else:
        pip_cmd = [str(venv_path / "bin" / "pip")]
        python_cmd = [str(venv_path / "bin" / "python")]
    
    # Install dependencies
    print_step("Installing dependencies...")
    try:
        # Upgrade pip
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install core dependencies first
        core_deps = [
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
            "typer>=0.9.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "structlog>=23.0.0"
        ]
        
        for dep in core_deps:
            subprocess.run(pip_cmd + ["install", dep], 
                          check=True, capture_output=True)
        
        # Install RA9 package
        subprocess.run(pip_cmd + ["install", "-e", "."], 
                      check=True, capture_output=True)
        
        print_success("Dependencies installed")
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return 1
    
    # Create .env file
    print_step("Creating configuration file...")
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# RA9 Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Configuration
RA9_DEFAULT_MODEL=gemini-pro
RA9_MAX_TOKENS=2048
RA9_TEMPERATURE=0.7
RA9_LOG_LEVEL=INFO
RA9_DEBUG=false
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print_success("Configuration file created (.env)")
        print_warning("Please edit .env file and add your GEMINI_API_KEY")
    else:
        print_success("Configuration file already exists")
    
    # Verify installation
    print_step("Verifying installation...")
    try:
        result = subprocess.run(
            python_cmd + ["-c", "import ra9; print('RA9 imported successfully')"],
            check=True, capture_output=True, text=True
        )
        print_success("RA9 package imported successfully")
        
        # Test CLI
        result = subprocess.run(
            python_cmd + ["-m", "ra9.cli", "--help"],
            check=True, capture_output=True, text=True
        )
        print_success("CLI is working")
        
    except subprocess.CalledProcessError as e:
        print_warning("CLI test failed (normal if API keys not configured)")
    
    # Print usage instructions
    print("\n🎉 Installation Complete!")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your GEMINI_API_KEY")
    print("2. Activate virtual environment:")
    
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n🚀 Usage Examples:")
    print(f"   {python_cmd[0]} -m ra9.cli process --query 'Hello, how are you?'")
    print(f"   {python_cmd[0]} -m ra9.cli interactive")
    print(f"   {python_cmd[0]} -m ra9.cli server --port 8000")
    
    print("\n📚 Documentation:")
    print("   README.md - Main documentation")
    print("   SETUP_GUIDE.md - Detailed setup guide")
    print("   CURRENT_BRANCH_README.md - Current branch specific info")
    
    print("\n🔑 Get API Key:")
    print("   https://aistudio.google.com/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
