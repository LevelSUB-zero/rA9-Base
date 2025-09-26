#!/usr/bin/env python3
"""
RA9 Installation Script

This script provides a robust installation process for RA9 that works across
different environments and platforms.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_colored(message: str, color: str = Colors.WHITE) -> None:
    """Print colored message."""
    print(f"{color}{message}{Colors.END}")


def print_header(message: str) -> None:
    """Print header message."""
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored(f"  {message}", Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)


def print_step(step: str, message: str) -> None:
    """Print step message."""
    print_colored(f"\n[{step}] {message}", Colors.BLUE)


def print_success(message: str) -> None:
    """Print success message."""
    print_colored(f"✓ {message}", Colors.GREEN)


def print_warning(message: str) -> None:
    """Print warning message."""
    print_colored(f"⚠ {message}", Colors.YELLOW)


def print_error(message: str) -> None:
    """Print error message."""
    print_colored(f"✗ {message}", Colors.RED)


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_pip() -> bool:
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print_success("pip is available")
        return True
    except subprocess.CalledProcessError:
        print_error("pip is not available")
        return False


def upgrade_pip() -> bool:
    """Upgrade pip to latest version."""
    try:
        print_step("1.1", "Upgrading pip...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        print_success("pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Failed to upgrade pip: {e}")
        return False


def install_build_tools() -> bool:
    """Install build tools if needed."""
    system = platform.system().lower()
    
    if system == "windows":
        print_step("1.2", "Checking Windows build tools...")
        try:
            # Try to import setuptools
            import setuptools
            print_success("Build tools already available")
            return True
        except ImportError:
            print_warning("Installing build tools for Windows...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "setuptools", "wheel", "setuptools-scm"
                ], check=True)
                print_success("Build tools installed")
                return True
            except subprocess.CalledProcessError:
                print_error("Failed to install build tools")
                return False
    
    return True


def create_virtual_environment(venv_path: Path) -> bool:
    """Create virtual environment."""
    try:
        print_step("2", f"Creating virtual environment at {venv_path}")
        
        if venv_path.exists():
            print_warning("Virtual environment already exists, removing...")
            shutil.rmtree(venv_path)
        
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True)
        
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_pip_command(venv_path: Optional[Path] = None) -> List[str]:
    """Get pip command for the environment."""
    if venv_path:
        if platform.system().lower() == "windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
        return [str(pip_path)]
    else:
        return [sys.executable, "-m", "pip"]


def install_dependencies(venv_path: Optional[Path] = None, dev: bool = False) -> bool:
    """Install project dependencies."""
    try:
        print_step("3", "Installing dependencies...")
        
        pip_cmd = get_pip_command(venv_path)
        
        # Upgrade pip first
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install the package in development mode
        if dev:
            subprocess.run(pip_cmd + ["install", "-e", ".[dev]"], 
                          check=True, cwd=Path.cwd())
            print_success("Development dependencies installed")
        else:
            subprocess.run(pip_cmd + ["install", "-e", "."], 
                          check=True, cwd=Path.cwd())
            print_success("Dependencies installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def create_env_file() -> bool:
    """Create .env file template."""
    try:
        print_step("4", "Creating environment configuration...")
        
        env_file = Path(".env")
        if env_file.exists():
            print_warning(".env file already exists, backing up...")
            shutil.copy(env_file, env_file.with_suffix(".env.backup"))
        
        env_content = """# RA9 Configuration
# Copy this file and fill in your API keys

# API Keys (required - set at least one)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
RA9_DEFAULT_MODEL=gemini-pro
RA9_MAX_TOKENS=2048
RA9_TEMPERATURE=0.7
RA9_MEMORY_ENABLED=true
RA9_MEMORY_PATH=memory
RA9_MAX_MEMORY_ENTRIES=1000
RA9_MAX_ITERATIONS=5
RA9_DEFAULT_MODE=concise
RA9_ENABLE_REFLECTION=true
RA9_LOG_LEVEL=INFO
RA9_DEBUG=false
RA9_DEV_MODE=false
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print_success("Environment file created (.env)")
        print_warning("Please edit .env file and add your API keys")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False


def verify_installation(venv_path: Optional[Path] = None) -> bool:
    """Verify installation."""
    try:
        print_step("5", "Verifying installation...")
        
        python_cmd = [sys.executable]
        if venv_path:
            if platform.system().lower() == "windows":
                python_cmd = [str(venv_path / "Scripts" / "python.exe")]
            else:
                python_cmd = [str(venv_path / "bin" / "python")]
        
        # Test import
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
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Verification failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def print_usage_instructions(venv_path: Optional[Path] = None) -> None:
    """Print usage instructions."""
    print_header("Installation Complete!")
    
    python_cmd = "python"
    if venv_path:
        if platform.system().lower() == "windows":
            python_cmd = str(venv_path / "Scripts" / "python.exe")
        else:
            python_cmd = str(venv_path / "bin" / "python")
    
    print_colored("\nUsage Instructions:", Colors.BOLD)
    print_colored("=" * 50, Colors.CYAN)
    
    print_colored("\n1. Configure API Keys:", Colors.YELLOW)
    print("   Edit the .env file and add your API keys:")
    print("   GEMINI_API_KEY=your_actual_api_key_here")
    
    print_colored("\n2. Basic Usage:", Colors.YELLOW)
    print(f"   {python_cmd} -m ra9.cli process --query 'Hello, how are you?'")
    print(f"   {python_cmd} -m ra9.cli interactive")
    print(f"   {python_cmd} -m ra9.cli server --port 8000")
    
    print_colored("\n3. Development Usage:", Colors.YELLOW)
    print(f"   {python_cmd} -m ra9.cli --debug process --query 'Test query'")
    print(f"   {python_cmd} -m pytest tests/")
    
    print_colored("\n4. Web Interface:", Colors.YELLOW)
    print("   Start the web server and visit http://localhost:8000")
    print(f"   {python_cmd} -m ra9.cli server")
    
    print_colored("\n5. Configuration:", Colors.YELLOW)
    print(f"   {python_cmd} -m ra9.cli config-info")
    
    print_colored("\nFor more information, visit:", Colors.CYAN)
    print("   https://github.com/LevelSUB-zero/rA9-Base")


def main():
    """Main installation function."""
    print_header("RA9 Ultra-Deep Cognitive Engine - Installation")
    
    # Parse command line arguments
    use_venv = "--venv" in sys.argv
    dev_mode = "--dev" in sys.argv
    skip_venv = "--no-venv" in sys.argv
    
    venv_path = None
    if use_venv and not skip_venv:
        venv_path = Path("venv")
    
    success = True
    
    # Step 1: Check prerequisites
    print_step("1", "Checking prerequisites...")
    if not check_python_version():
        success = False
    if not check_pip():
        success = False
    if not success:
        print_error("Prerequisites check failed")
        return 1
    
    upgrade_pip()
    install_build_tools()
    
    # Step 2: Create virtual environment (if requested)
    if venv_path and not skip_venv:
        if not create_virtual_environment(venv_path):
            success = False
    
    # Step 3: Install dependencies
    if not install_dependencies(venv_path, dev_mode):
        success = False
    
    # Step 4: Create configuration
    if not create_env_file():
        success = False
    
    # Step 5: Verify installation
    if not verify_installation(venv_path):
        success = False
    
    if success:
        print_usage_instructions(venv_path)
        return 0
    else:
        print_error("Installation failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
