# RA9 Ultra-Deep Cognitive Engine - Current Branch

## 🚀 Latest Stable Version

This is the **Current** branch containing the most up-to-date, tested, and stable version of RA9 with all professional improvements and fixes.

## ✨ What's New in Current Branch

- ✅ **Professional Package Structure** - Modern Python packaging with `pyproject.toml`
- ✅ **Robust Installation Script** - Fixed dependency handling and verification
- ✅ **CLI Interface** - Command-line interface with `typer`
- ✅ **Web Server** - FastAPI-based web interface
- ✅ **Configuration Management** - Pydantic v2 settings with environment variables
- ✅ **Structured Logging** - Professional logging with `structlog`
- ✅ **Memory Management** - Episodic, semantic, and reflective memory
- ✅ **Agent Architecture** - Modular agent system with base classes
- ✅ **Quality Controls** - Pre-commit hooks, linting, testing
- ✅ **Cross-Platform** - Works on Windows, macOS, and Linux

## 🛠️ Quick Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base

# Switch to Current branch
git checkout Current

# Run the automated installer
python install.py --venv
```

### Option 2: Manual Installation

```bash
# Clone and switch to Current branch
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base
git checkout Current

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .

# Create environment file
cp env.example .env
# Edit .env and add your API keys
```

## 🔑 Configuration

### Required: API Keys

Edit the `.env` file and add your API keys:

```bash
# Required - Get from Google AI Studio
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_api_key_here
```

### Get Gemini API Key:
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create a new API key
4. Copy and paste into `.env` file

## 🎯 Usage

### Command Line Interface

```bash
# Basic query
python -m ra9.cli process --query "What is artificial intelligence?"

# Interactive mode
python -m ra9.cli interactive

# Web server
python -m ra9.cli server --port 8000

# Help
python -m ra9.cli --help
```

### Python API

```python
from ra9.core.cli_workflow_engine import run_cli_workflow

# Define your query
query = {
    "jobId": "test-1",
    "text": "Explain quantum computing",
    "mode": "deep",
    "loopDepth": 2,
    "allowMemoryWrite": True
}

# Run the workflow
result = run_cli_workflow(query)
print(result["final_answer"])
```

### Web Interface

```bash
# Start web server
python -m ra9.cli server

# Visit http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 🏗️ Architecture

```
RA9 Cognitive Architecture
├── Core Engine (ra9/core/)
│   ├── engine.py              # Main cognitive orchestrator
│   ├── config.py              # Configuration management
│   ├── logger.py              # Structured logging
│   └── schemas.py             # Data structures
├── Agents (ra9/agents/)
│   ├── base_agent.py          # Base agent class
│   ├── logic_agent.py         # Logical reasoning
│   ├── emotion_agent.py       # Emotional processing
│   ├── creative_agent.py      # Creative generation
│   └── strategy_agent.py      # Strategic planning
├── Memory (ra9/memory/)
│   ├── memory_manager.py     # Memory orchestration
│   ├── episodic_memory.py    # Episodic memory
│   ├── semantic_memory.py     # Semantic memory
│   └── reflective_memory.py  # Reflective memory
├── Tools (ra9/tools/)
│   ├── search_agent.py        # Web search
│   └── tool_api.py           # Tool integration
└── Router (ra9/router/)
    ├── query_classifier.py    # Query classification
    └── context_preprocessor.py # Context processing
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ra9

# Run specific tests
pytest tests/test_quality_guards.py
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
python install.py --venv --dev

# Or manually:
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black ra9/

# Lint code
flake8 ra9/

# Type checking
mypy ra9/

# Run pre-commit hooks
pre-commit run --all-files
```

### Make Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Start web server
make serve
```

## 🚨 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'pydantic'**
   ```bash
   # Solution: Use the automated installer
   python install.py --venv
   ```

2. **API Key Not Found**
   ```bash
   # Solution: Add API key to .env file
   echo "GEMINI_API_KEY=your_key_here" >> .env
   ```

3. **Permission Denied**
   ```bash
   # Solution: Check file permissions or use virtual environment
   python install.py --venv
   ```

4. **Import Errors**
   ```bash
   # Solution: Ensure virtual environment is activated
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

### Debug Mode

```bash
# Enable debug logging
export RA9_DEBUG=true
python -m ra9.cli process --query "test query"
```

## 📊 Quality Metrics

```python
from ra9.core.cli_quality_summary import run_quality_summary

# Get quality metrics
metrics = run_quality_summary()
print(f"Broadcast Count: {metrics['broadcast_count']}")
print(f"Quarantine Count: {metrics['quarantine_count']}")
print(f"Coherence Score: {metrics['coherence']}")
```

## 🔄 Updates

To get the latest updates:

```bash
# Pull latest changes
git pull origin Current

# Reinstall if needed
python install.py --venv
```

## 📚 Documentation

- **Setup Guide**: `SETUP_GUIDE.md`
- **Architecture**: `ARCHITECTURE.md`
- **Contributing**: `CONTRIBUTING.md`
- **Release Notes**: `RELEASE_NOTES.md`

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/LevelSUB-zero/rA9-Base/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LevelSUB-zero/rA9-Base/discussions)

## 📄 License

MIT License - see `LICENSE` file for details.

---

**RA9 Development Team** - Building the future of cognitive AI

*Current Branch - Latest Stable Version*
