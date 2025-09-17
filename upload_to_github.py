#!/usr/bin/env python3
"""
RA9 GitHub Upload Script
Automated script to upload RA9 to GitHub repository
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_git_status():
    """Check if we're in a git repository"""
    print("🔍 Checking Git status...")
    
    # Check if .git exists
    if not Path(".git").exists():
        print("❌ Not in a Git repository. Initializing...")
        if not run_command("git init", "Initialize Git repository"):
            return False
    
    # Check if remote exists
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" not in result.stdout:
        print("❌ No origin remote found. Adding...")
        if not run_command("git remote add origin https://github.com/LevelSUB-zero/rA9-Base.git", "Add origin remote"):
            return False
    
    print("✅ Git repository ready")
    return True

def prepare_files():
    """Prepare files for upload"""
    print("📁 Preparing files for upload...")
    
    # Ensure all necessary files exist
    required_files = [
        "README.md",
        "ARCHITECTURE.md",
        "CONTRIBUTING.md",
        "SETUP_GUIDE.md",
        "setup_ra9.py",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "env.example",
        ".gitignore"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def commit_and_push():
    """Commit changes and push to GitHub"""
    print("📤 Committing and pushing to GitHub...")
    
    # Add all files
    if not run_command("git add .", "Add all files"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("ℹ️  No changes to commit")
        return True
    
    # Commit changes
    commit_message = """Initial RA9 Cognitive Engine upload

- Complete multi-agent cognitive architecture
- Quality assurance pipeline with self-critique
- Global workspace and meta-coherence validation
- Comprehensive testing and documentation
- Automated setup and configuration
- Examples and usage guides

Features:
- Logical, Emotional, Creative, and Strategic agents
- Quality gates and quarantine system
- Memory integration and context management
- Neuromodulation and attention control
- Comprehensive test suite and quality metrics

Ready for development and collaboration!"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Commit changes"):
        return False
    
    # Push to GitHub
    if not run_command("git push -u origin main", "Push to GitHub"):
        return False
    
    print("✅ Successfully uploaded to GitHub!")
    return True

def verify_upload():
    """Verify the upload was successful"""
    print("🔍 Verifying upload...")
    
    # Check if we can fetch from remote
    if not run_command("git fetch origin", "Fetch from remote"):
        return False
    
    # Check if local and remote are in sync
    result = subprocess.run("git status -uno", shell=True, capture_output=True, text=True)
    if "Your branch is up to date" not in result.stdout:
        print("⚠️  Local and remote may not be in sync")
        return False
    
    print("✅ Upload verified successfully")
    return True

def create_release_notes():
    """Create release notes for the initial upload"""
    print("📝 Creating release notes...")
    
    release_notes = """# RA9 Cognitive Engine v0.1.0 - Initial Release

## 🧠 What is RA9?

RA9 is an advanced multi-agent cognitive architecture inspired by brain-like processing. It implements a sophisticated system of specialized agents that work together through a global workspace, with quality gates, self-critique mechanisms, and meta-coherence validation.

## ✨ Key Features

- **Multi-Agent Architecture**: Specialized cognitive agents (Logical, Emotional, Creative, Strategic)
- **Quality Assurance**: Built-in critique system with automatic rewrite capabilities
- **Global Workspace**: Centralized information sharing and conflict resolution
- **Memory Integration**: Persistent episodic and semantic memory systems
- **Neuromodulation**: Dynamic attention and exploration control
- **Comprehensive Testing**: Automated quality guards and integration tests

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/LevelSUB-zero/rA9-Base.git
   cd rA9-Base
   ```

2. Run the automated setup:
   ```bash
   python setup_ra9.py
   ```

3. Test the installation:
   ```bash
   python examples/test_runner.py
   ```

## 📚 Documentation

- **README.md**: Complete setup and usage guide
- **ARCHITECTURE.md**: Detailed system architecture
- **SETUP_GUIDE.md**: Comprehensive setup instructions
- **CONTRIBUTING.md**: Guidelines for contributors

## 🔧 Configuration

1. Copy `env.example` to `.env`
2. Add your Gemini API key to `.env`
3. Customize settings as needed

## 🧪 Testing

Run the comprehensive test suite:
```bash
python examples/test_runner.py
```

## 🤝 Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by Global Workspace Theory and cognitive architectures
- Built with LangChain and modern AI frameworks
- Community contributions and feedback

---

**RA9 Development Team** - Building the future of cognitive AI"""
    
    with open("RELEASE_NOTES.md", "w") as f:
        f.write(release_notes)
    
    print("✅ Release notes created")
    return True

def main():
    """Main upload function"""
    print("🚀 RA9 GitHub Upload Script")
    print("=" * 50)
    print("This script will upload RA9 to the GitHub repository")
    print("=" * 50)
    
    try:
        # Check prerequisites
        if not check_git_status():
            print("❌ Git setup failed")
            return False
        
        # Prepare files
        if not prepare_files():
            print("❌ File preparation failed")
            return False
        
        # Create release notes
        if not create_release_notes():
            print("❌ Release notes creation failed")
            return False
        
        # Commit and push
        if not commit_and_push():
            print("❌ Upload failed")
            return False
        
        # Verify upload
        if not verify_upload():
            print("❌ Upload verification failed")
            return False
        
        print("\n🎉 RA9 successfully uploaded to GitHub!")
        print("\nNext steps:")
        print("1. Visit: https://github.com/LevelSUB-zero/rA9-Base")
        print("2. Share with your colleagues")
        print("3. Start collaborating!")
        print("4. Check the Issues tab for any problems")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ Upload cancelled by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Upload failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
