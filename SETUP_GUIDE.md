# RA9 Setup Guide

This guide will help you set up RA9 on any system with minimal issues.

## 🚀 Quick Start (Recommended)

### 1. Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **pip** (latest version)
- **Git** (for cloning)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base

# Run the automated installer
python install.py

# Or for development
python install.py --dev
```

### 3. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

### 4. Test Installation

```bash
# Test basic functionality
ra9 config-info

# Test with a query
ra9 process --query "Hello, how are you?"
```

## 🔧 Manual Installation

If the automated installer doesn't work, follow these steps:

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install RA9
pip install -e ".[dev]"
```

### 3. Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit configuration
# Add your API keys to .env file
```

## 🌐 Platform-Specific Instructions

### Windows

1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Enable Developer Mode** (optional, for better performance)
3. **Use PowerShell** or **Command Prompt**
4. **Run as Administrator** if you encounter permission issues

```powershell
# In PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python install.py
```

### macOS

1. **Install Python** using Homebrew:
   ```bash
   brew install python@3.9
   ```

2. **Install Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

3. **Run installation**:
   ```bash
   python3 install.py
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3.9 python3.9-venv python3.9-dev build-essential
   ```

2. **Install RA9**:
   ```bash
   python3 install.py
   ```

### Linux (CentOS/RHEL)

1. **Install Python and dependencies**:
   ```bash
   sudo yum install python39 python39-devel gcc gcc-c++ make
   ```

2. **Install RA9**:
   ```bash
   python3 install.py
   ```

## 🔑 API Key Configuration

### Google Gemini (Recommended)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### OpenAI (Alternative)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to your `.env` file:
   ```env
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## 🧪 Testing Your Installation

### Basic Test

```bash
# Test CLI
ra9 --help

# Test configuration
ra9 config-info

# Test query processing
ra9 process --query "What is 2+2?" --mode concise
```

### Advanced Test

```bash
# Test interactive mode
ra9 interactive

# Test web server
ra9 server --port 8000
# Visit http://localhost:8000 in your browser
```

### Python API Test

```python
# test_ra9.py
from ra9 import run_ra9_cognitive_engine, get_config

# Test configuration
config = get_config()
print(f"Configured: {config.is_configured()}")

# Test query processing
result = run_ra9_cognitive_engine(
    job_id="test_001",
    job_payload={
        "text": "Explain quantum computing in simple terms",
        "mode": "concise",
        "loopDepth": 1,
        "allowMemoryWrite": False
    }
)

print(f"Result: {result.get('final_answer', 'No result')}")
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError` or import errors

**Solutions**:
```bash
# Reinstall in development mode
pip install -e ".[dev]" --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"

# Verify installation
python -c "import ra9; print(ra9.__version__)"
```

#### 2. API Key Errors

**Problem**: "No API keys configured" error

**Solutions**:
```bash
# Check .env file exists
ls -la .env

# Check environment variables
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# Test with explicit key
GEMINI_API_KEY=your_key ra9 process --query "test"
```

#### 3. Permission Errors

**Problem**: Permission denied errors

**Solutions**:
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with user flag
pip install -e ".[dev]" --user
```

#### 4. Memory/Storage Errors

**Problem**: Memory directory not writable

**Solutions**:
```bash
# Create memory directory
mkdir -p memory
chmod 755 memory

# Check permissions
ls -la memory/
```

#### 5. Dependency Conflicts

**Problem**: Package version conflicts

**Solutions**:
```bash
# Create fresh environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Or use conda
conda create -n ra9 python=3.9
conda activate ra9
pip install -e ".[dev]"
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# CLI debug mode
ra9 --debug process --query "test query"

# Python debug mode
RA9_DEBUG=true python -c "import ra9; print('Debug mode enabled')"
```

### Logs

Check logs for detailed error information:

```bash
# Check log files
ls -la *.log

# View recent logs
tail -f ra9.log

# Check system logs (Linux/Mac)
journalctl -u ra9
```

## 🔄 Updating RA9

### Update from Git

```bash
# Pull latest changes
git pull origin main

# Reinstall
pip install -e ".[dev]" --force-reinstall

# Update dependencies
pip install -e ".[dev]" --upgrade
```

### Update from PyPI (when available)

```bash
pip install --upgrade ra9-ai
```

## 🚀 Performance Optimization

### Memory Optimization

```bash
# Increase memory limits
export RA9_MAX_MEMORY_ENTRIES=5000

# Use faster storage
export RA9_MEMORY_PATH=/tmp/ra9_memory
```

### CPU Optimization

```bash
# Limit concurrent agents
export RA9_MAX_CONCURRENT_AGENTS=2

# Adjust timeout
export RA9_TIMEOUT_SECONDS=60
```

### Network Optimization

```bash
# Use local models (if available)
export RA9_DEFAULT_MODEL=local-model

# Adjust request timeout
export RA9_TIMEOUT_SECONDS=30
```

## 📊 Monitoring

### Health Check

```bash
# Check system health
ra9 config-info

# Test API connectivity
curl -X GET http://localhost:8000/health
```

### Performance Monitoring

```bash
# Monitor memory usage
ps aux | grep ra9

# Monitor CPU usage
top -p $(pgrep -f ra9)

# Monitor disk usage
du -sh memory/
```

## 🆘 Getting Help

### Documentation

- [README.md](README.md) - Main documentation
- [API Documentation](http://localhost:8000/docs) - Web API docs
- [Examples](examples/) - Usage examples

### Support Channels

- **GitHub Issues**: [Report bugs](https://github.com/LevelSUB-zero/rA9-Base/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/LevelSUB-zero/rA9-Base/discussions)
- **Email**: contact@ra9.ai

### Community

- Join our Discord server (if available)
- Follow us on Twitter (if available)
- Star the repository on GitHub

---

**Need more help?** Check the [troubleshooting section](#-troubleshooting) or [open an issue](https://github.com/LevelSUB-zero/rA9-Base/issues).