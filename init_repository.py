#!/usr/bin/env python3
"""
RA9 Repository Initialization Script
Prepares the RA9 project for GitHub upload
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"⚠️  {description} completed with warnings")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def initialize_git_repository():
    """Initialize Git repository if not already initialized"""
    print("🔧 Initializing Git repository...")
    
    if Path(".git").exists():
        print("✅ Git repository already exists")
        return True
    
    # Initialize Git repository
    if not run_command("git init", "Initialize Git repository"):
        return False
    
    # Set default branch to main
    if not run_command("git branch -M main", "Set default branch to main"):
        return False
    
    return True

def setup_git_remote():
    """Setup Git remote for GitHub repository"""
    print("🌐 Setting up Git remote...")
    
    # Check if origin already exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" in result.stdout:
        print("✅ Origin remote already exists")
        return True
    
    # Add origin remote
    if not run_command("git remote add origin https://github.com/LevelSUB-zero/rA9-Base.git", "Add origin remote"):
        return False
    
    return True

def create_initial_commit():
    """Create initial commit with all files"""
    print("📝 Creating initial commit...")
    
    # Add all files
    if not run_command("git add .", "Add all files to staging"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("ℹ️  No changes to commit")
        return True
    
    # Create initial commit
    commit_message = """Initial RA9 Cognitive Engine commit

Complete multi-agent cognitive architecture with:

Core Features:
- Multi-agent system (Logical, Emotional, Creative, Strategic)
- Global workspace and meta-coherence validation
- Quality assurance pipeline with self-critique
- Memory integration and context management
- Neuromodulation and attention control

Quality Assurance:
- Comprehensive test suite
- Automated quality guards
- Quarantine system for failed outputs
- Confidence scoring and validation

Documentation:
- Complete setup and usage guides
- Architecture documentation
- Contributing guidelines
- Examples and tutorials

Development Tools:
- Automated setup script
- Test runners and quality metrics
- Configuration management
- Git integration

Ready for collaborative development! 🧠✨"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Create initial commit"):
        return False
    
    return True

def verify_repository_structure():
    """Verify that all required files are present"""
    print("🔍 Verifying repository structure...")
    
    required_files = [
        "README.md",
        "ARCHITECTURE.md",
        "CONTRIBUTING.md",
        "SETUP_GUIDE.md",
        "PROJECT_SUMMARY.md",
        "setup_ra9.py",
        "upload_to_github.py",
        "init_repository.py",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "env.example",
        ".gitignore"
    ]
    
    required_directories = [
        "ra9",
        "ra9/core",
        "ra9/agents",
        "ra9/memory",
        "ra9/tools",
        "tests",
        "examples"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    missing_dirs = []
    for directory in required_directories:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    if missing_dirs:
        print(f"❌ Missing required directories: {missing_dirs}")
        return False
    
    print("✅ Repository structure verified")
    return True

def create_gitignore():
    """Ensure .gitignore is properly configured"""
    print("📋 Verifying .gitignore configuration...")
    
    if not Path(".gitignore").exists():
        print("❌ .gitignore file missing")
        return False
    
    # Check if .gitignore contains essential patterns
    with open(".gitignore", "r") as f:
        content = f.read()
    
    essential_patterns = [
        "__pycache__",
        "*.pyc",
        ".env",
        "ra9_env",
        "memory/",
        "*.log"
    ]
    
    missing_patterns = []
    for pattern in essential_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"⚠️  .gitignore missing patterns: {missing_patterns}")
        print("Consider adding these patterns to .gitignore")
    
    print("✅ .gitignore configuration verified")
    return True

def prepare_for_upload():
    """Prepare repository for GitHub upload"""
    print("🚀 Preparing repository for GitHub upload...")
    
    # Verify repository structure
    if not verify_repository_structure():
        return False
    
    # Verify .gitignore
    if not create_gitignore():
        return False
    
    # Initialize Git if needed
    if not initialize_git_repository():
        return False
    
    # Setup remote
    if not setup_git_remote():
        return False
    
    # Create initial commit
    if not create_initial_commit():
        return False
    
    print("✅ Repository ready for GitHub upload!")
    return True

def show_next_steps():
    """Show next steps for uploading to GitHub"""
    print("\n🎉 Repository initialization complete!")
    print("\nNext steps to upload to GitHub:")
    print("=" * 50)
    
    print("\n1. Push to GitHub:")
    print("   git push -u origin main")
    
    print("\n2. Or use the automated upload script:")
    print("   python upload_to_github.py")
    
    print("\n3. Verify upload:")
    print("   Visit: https://github.com/LevelSUB-zero/rA9-Base")
    
    print("\n4. Share with colleagues:")
    print("   Send them the repository URL and setup guide")
    
    print("\n5. Start collaborating:")
    print("   - Create issues for bugs and features")
    print("   - Create pull requests for contributions")
    print("   - Use GitHub Discussions for questions")
    
    print("\n📚 Documentation available:")
    print("   - README.md: Complete setup guide")
    print("   - SETUP_GUIDE.md: Detailed instructions")
    print("   - ARCHITECTURE.md: System architecture")
    print("   - CONTRIBUTING.md: Contribution guidelines")
    print("   - PROJECT_SUMMARY.md: Project overview")
    
    print("\n🧪 Testing:")
    print("   python examples/test_runner.py")
    
    print("\n🚀 Examples:")
    print("   python examples/basic_usage.py")
    print("   python examples/advanced_usage.py")

def main():
    """Main initialization function"""
    print("🧠 RA9 Repository Initialization")
    print("=" * 50)
    print("This script will prepare RA9 for GitHub upload")
    print("=" * 50)
    
    try:
        # Prepare repository
        if not prepare_for_upload():
            print("❌ Repository preparation failed")
            return False
        
        # Show next steps
        show_next_steps()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ Initialization cancelled by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Initialization failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
