# RA9 Setup Guide for Developers

This comprehensive guide will help your colleagues set up and run the RA9 Cognitive Engine from scratch.

## 🚀 Quick Start (5 minutes)

### Prerequisites Check
```bash
# Check Python version (requires 3.8+)
python --version

# Check if pip is available
pip --version

# Check if git is available
git --version
```

### One-Command Setup
```bash
# Clone and setup in one go
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base
python setup_ra9.py
```

## 📋 Detailed Setup Instructions

### Step 1: Environment Preparation

#### Windows
```powershell
# Open PowerShell as Administrator
# Install Python 3.8+ from python.org if not installed

# Verify installation
python --version
pip --version

# Create project directory
mkdir C:\ra9-dev
cd C:\ra9-dev
```

#### macOS
```bash
# Install Python 3.8+ using Homebrew
brew install python@3.9

# Or download from python.org
# Verify installation
python3 --version
pip3 --version

# Create project directory
mkdir ~/ra9-dev
cd ~/ra9-dev
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3.8+ and pip
sudo apt install python3.9 python3.9-pip python3.9-venv

# Verify installation
python3.9 --version
pip3 --version

# Create project directory
mkdir ~/ra9-dev
cd ~/ra9-dev
```

### Step 2: Repository Setup

```bash
# Clone the repository
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base

# Verify repository structure
ls -la
# Should see: README.md, setup_ra9.py, ra9/, tests/, examples/
```

### Step 3: Virtual Environment Setup

#### Windows
```powershell
# Create virtual environment
python -m venv ra9_env

# Activate virtual environment
ra9_env\Scripts\activate

# Verify activation (should show (ra9_env) in prompt)
# Upgrade pip
python -m pip install --upgrade pip
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv ra9_env

# Activate virtual environment
source ra9_env/bin/activate

# Verify activation (should show (ra9_env) in prompt)
# Upgrade pip
python -m pip install --upgrade pip
```

### Step 4: Dependencies Installation

#### Option A: Automated Setup (Recommended)
```bash
# Run the automated setup script
python setup_ra9.py
```

#### Option B: Manual Installation
```bash
# Install core package
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Or install from requirements files
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 5: Environment Configuration

#### Create .env file
```bash
# Create .env file
touch .env  # Linux/macOS
# or
echo. > .env  # Windows
```

#### Add API Key
```bash
# Edit .env file and add your Gemini API key
echo "GEMINI_API_KEY=your_actual_api_key_here" >> .env
```

#### Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your .env file

### Step 6: Verify Installation

#### Run Test Suite
```bash
# Run comprehensive tests
python examples/test_runner.py

# Expected output:
# ✅ All critical imports successful
# ✅ All pytest tests passed!
# ✅ All test categories passed
```

#### Run Basic Example
```bash
# Test basic functionality
python examples/basic_usage.py

# Expected output:
# 🤖 Running RA9 with example query...
# Query: What is artificial intelligence?
# 📝 RA9 Response: [AI response]
```

#### Test CLI Interface
```bash
# Test command line interface
echo '{"jobId":"test","text":"Hello RA9!","mode":"deep"}' | python ra9/main.py

# Expected output: JSON response with AI-generated content
```

## 🔧 Configuration Options

### Environment Variables (.env file)

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Logging
RA9_LOG_LEVEL=INFO
RA9_DEBUG=false

# Optional - Memory and Storage
RA9_MEMORY_PATH=./memory
RA9_MAX_ITERATIONS=5

# Optional - Quality Control
RA9_CRITIC_MAX_ISSUES=0
RA9_COHERENCE_THRESHOLD=0.85
```

### Configuration Files

#### ra9/core/config.py
```python
# System-wide configuration
CRITIC_MAX_ALLOWED_ISSUES = 0      # Quality control strictness
COHERENCE_THRESHOLD = 0.85         # Coherence requirement
MAX_ITERATIONS = 5                 # Maximum processing iterations
```

#### ra9/core/self_persona.yaml
```yaml
# RA9's personality and behavior settings
name: "RA9"
core_values: ["Seek understanding", "Reflect deeply", "Evolve with experience"]
identity_traits: ["Curious", "Empathetic", "Strategic"]
```

## 🧪 Testing and Validation

### Run All Tests
```bash
# Comprehensive test suite
python examples/test_runner.py

# Individual test categories
pytest tests/test_quality_guards.py -v
pytest tests/test_integration_quality.py -v
pytest ra9/test_complete_brain_architecture.py -v
```

### Quality Metrics
```bash
# Get system quality metrics
python -c "from ra9.core.cli_quality_summary import run_quality_summary; print(run_quality_summary())"
```

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/ --benchmark-only

# Memory profiling
python -m memory_profiler examples/advanced_usage.py
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Python Version Issues
```bash
# Problem: Python version too old
# Solution: Install Python 3.8+
python --version  # Should show 3.8+

# If using python3 command
python3 --version
```

#### 2. Virtual Environment Issues
```bash
# Problem: Virtual environment not activating
# Solution: Use full path or recreate

# Windows
ra9_env\Scripts\activate.bat

# macOS/Linux
source ra9_env/bin/activate

# If still not working, recreate
rm -rf ra9_env
python -m venv ra9_env
```

#### 3. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Ensure virtual environment is activated and package installed

# Check if in virtual environment
which python  # Should show path to ra9_env

# Reinstall package
pip install -e .
```

#### 4. API Key Issues
```bash
# Problem: GEMINI_API_KEY not found
# Solution: Check .env file

# Verify .env file exists and has correct key
cat .env
# Should show: GEMINI_API_KEY=your_key_here

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('GEMINI_API_KEY')[:10] + '...')"
```

#### 5. Permission Issues
```bash
# Problem: Permission denied errors
# Solution: Check file permissions

# Linux/macOS
chmod +x setup_ra9.py
chmod +x examples/*.py

# Windows: Run PowerShell as Administrator
```

#### 6. Memory Issues
```bash
# Problem: Out of memory errors
# Solution: Reduce memory usage

# Edit ra9/core/config.py
MAX_ITERATIONS = 2  # Reduce from 5
MEMORY_CACHE_SIZE = 500  # Reduce from 1000
```

### Debug Mode

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verbose Test Output
```bash
# Run tests with verbose output
pytest -v -s

# Run specific test with debug output
pytest tests/test_specific.py -v -s --log-cli-level=DEBUG
```

#### Interactive Debugging
```python
# Add breakpoints in code
import ipdb; ipdb.set_trace()

# Or use pdb
import pdb; pdb.set_trace()
```

## 📚 Next Steps

### 1. Explore Examples
```bash
# Run all examples
python examples/advanced_usage.py

# Run specific examples
python examples/basic_usage.py
```

### 2. Read Documentation
- **README.md**: Complete overview and usage guide
- **ARCHITECTURE.md**: Detailed system architecture
- **CONTRIBUTING.md**: Guidelines for contributing

### 3. Start Developing
```bash
# Create your own agent
cp ra9/agents/logic_agent.py ra9/agents/custom_agent.py
# Edit custom_agent.py with your logic

# Create your own test
cp tests/test_quality_guards.py tests/test_custom_agent.py
# Edit test_custom_agent.py with your tests
```

### 4. Join the Community
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute improvements

## 🆘 Getting Help

### Self-Help Resources
1. **Check this guide** for common issues
2. **Read the documentation** in README.md and ARCHITECTURE.md
3. **Run the test suite** to verify your setup
4. **Check the examples** for usage patterns

### Community Support
1. **GitHub Issues**: For bug reports and feature requests
2. **GitHub Discussions**: For questions and general discussion
3. **Code Review**: For help with contributions

### Emergency Debugging
```bash
# Quick health check
python -c "
import ra9
from ra9.core.schemas import AgentOutput
from ra9.core.engine import CognitiveEngine
print('✅ Basic imports successful')
"

# Test API connectivity
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('GEMINI_API_KEY')
print(f'API Key: {\"✅ Found\" if key else \"❌ Missing\"}')
"

# Test basic functionality
python -c "
from ra9.test_complete_brain_architecture import test_complete_brain_workflow
result = test_complete_brain_workflow('test query')
print(f'Test result: {\"✅ Success\" if result.get(\"success\") else \"❌ Failed\"}')
"
```

## 🎉 Success!

If you've followed this guide successfully, you should now have:
- ✅ RA9 installed and configured
- ✅ Virtual environment set up
- ✅ API key configured
- ✅ Tests passing
- ✅ Examples running
- ✅ Ready to develop!

Welcome to the RA9 development team! 🧠✨
