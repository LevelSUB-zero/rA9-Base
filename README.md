# RA9 - Ultra-Deep Cognitive Engine

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A sophisticated multi-agent cognitive architecture designed for advanced AI reasoning, problem-solving, and decision-making. RA9 combines multiple specialized cognitive agents to provide deep, contextual understanding and intelligent responses.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for logic, emotion, creativity, strategy, and meta-cognition
- **Advanced Memory System**: Episodic, semantic, and reflective memory capabilities
- **Intelligent Query Routing**: Automatic classification and routing to appropriate agents
- **Flexible Interfaces**: CLI, web API, and interactive modes
- **Robust Configuration**: Environment-based configuration with validation
- **Professional Structure**: Industry-standard packaging and development practices

## 🏗️ Architecture

RA9 consists of several specialized cognitive agents:

- **Logic Agent**: Logical reasoning and analytical thinking
- **Emotion Agent**: Emotional intelligence and empathy
- **Creative Agent**: Creative thinking and ideation
- **Strategic Agent**: Strategic planning and decision-making
- **Meta-Coherence Agent**: Meta-cognitive reflection and coherence
- **Feedback Agent**: Continuous improvement and learning

## 📦 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/LevelSUB-zero/rA9-Base.git
cd rA9-Base

# Run the installation script
python install.py

# Or for development
python install.py --dev
```

### Manual Install

```bash
# Install in development mode
pip install -e ".[dev]"

# Or install with specific dependencies
pip install -e ".[docs,test]"
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install RA9
pip install -e ".[dev]"
```

## ⚙️ Configuration

1. **Copy the environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` and add your API keys:**
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   # OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Configure additional settings (optional):**
   ```env
   RA9_DEFAULT_MODEL=gemini-pro
   RA9_MAX_TOKENS=2048
   RA9_TEMPERATURE=0.7
   RA9_MEMORY_ENABLED=true
   RA9_LOG_LEVEL=INFO
   ```

## 🚀 Usage

### Command Line Interface

```bash
# Process a single query
ra9 process --query "What is the meaning of life?" --mode creative

# Interactive mode
ra9 interactive

# Start web server
ra9 server --port 8000

# Show configuration
ra9 config-info
```

### Python API

```python
from ra9 import run_ra9_cognitive_engine, get_config

# Configure
config = get_config()

# Process query
result = run_ra9_cognitive_engine(
    job_id="test_001",
    job_payload={
        "text": "Explain quantum computing",
        "mode": "detailed",
        "loopDepth": 3,
        "allowMemoryWrite": True
    }
)

print(result["final_answer"])
```

### Web API

Start the server:
```bash
ra9 server
```

Then make requests:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is artificial intelligence?",
    "mode": "concise",
    "loop_depth": 1
  }'
```

## 🧪 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black ra9/
isort ra9/
flake8 ra9/
mypy ra9/
```

### Project Structure

```
ra9/
├── agents/           # Cognitive agents
├── core/            # Core engine and configuration
├── memory/          # Memory management
├── router/          # Query classification and routing
├── tools/           # Tools and utilities
├── cli.py           # Command line interface
├── server.py        # Web server
└── main.py          # Legacy entry point
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`:
   ```python
   from ra9.agents.base_agent import BaseAgent, AgentResult
   
   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__("MyAgent", "Description of my agent")
       
       def process_query(self, query: str, context: Dict[str, Any]) -> AgentResult:
           # Implement your agent logic
           return AgentResult(
               answer="My response",
               quality_score=8.5,
               confidence=0.9
           )
   ```

2. Register the agent in the routing system
3. Add tests for your agent

## 📊 Performance

RA9 is designed for high performance with:

- **Concurrent Processing**: Multiple agents can work in parallel
- **Memory Optimization**: Efficient memory storage and retrieval
- **Caching**: Intelligent caching of responses and computations
- **Streaming**: Real-time response streaming for better UX

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the correct directory and have installed the package
2. **API Key Errors**: Verify your API keys are set in the `.env` file
3. **Memory Issues**: Check that the memory directory is writable
4. **Dependency Issues**: Try reinstalling with `pip install -e ".[dev]" --force-reinstall`

### Debug Mode

Enable debug mode for detailed logging:
```bash
ra9 --debug process --query "test query"
```

### Logs

Check logs in the configured log file or console output for detailed error information.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain for the AI framework
- FastAPI for the web interface
- Pydantic for data validation
- Rich for beautiful CLI output

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/LevelSUB-zero/rA9-Base/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LevelSUB-zero/rA9-Base/discussions)
- **Email**: contact@ra9.ai

---

**RA9** - *Where Intelligence Meets Imagination*