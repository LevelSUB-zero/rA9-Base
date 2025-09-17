# RA9 - Ultra-Deep Cognitive Engine

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/LevelSUB-zero/rA9-Base)

## 🧠 What is RA9?

RA9 is an advanced multi-agent cognitive architecture inspired by brain-like processing. It implements a sophisticated system of specialized agents (Logical, Emotional, Creative, Strategic) that work together through a global workspace, with quality gates, self-critique mechanisms, and meta-coherence validation.

### Key Features

- **Multi-Agent Architecture**: Specialized cognitive agents with distinct roles
- **Quality Assurance**: Built-in critique system with automatic rewrite capabilities
- **Global Workspace**: Centralized information sharing and conflict resolution
- **Memory Integration**: Persistent episodic and semantic memory systems
- **Neuromodulation**: Dynamic attention and exploration control
- **Comprehensive Testing**: Automated quality guards and integration tests

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for LLM functionality)
- Git (for cloning the repository)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LevelSUB-zero/rA9-Base.git
   cd rA9-Base
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv ra9_env
   
   # On Windows:
   ra9_env\Scripts\activate
   
   # On macOS/Linux:
   source ra9_env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   ```

5. **Run the setup script:**
   ```bash
   python setup_ra9.py
   ```

### Basic Usage

#### Command Line Interface

```bash
# Simple query
echo '{"jobId":"test-1","text":"What is artificial intelligence?","mode":"deep"}' | python ra9/main.py

# Complex query with specific parameters
echo '{"jobId":"complex-1","text":"Design a sustainable city for 2050","mode":"hybrid","loopDepth":3,"allowMemoryWrite":true}' | python ra9/main.py
```

#### Python API

```python
from ra9.core.cli_workflow_engine import run_cli_workflow

# Define your query
query = {
    "jobId": "api-test",
    "text": "Explain quantum computing in simple terms",
    "mode": "deep",
    "loopDepth": 2,
    "allowMemoryWrite": False
}

# Run the workflow
result = run_cli_workflow(query)
print(result["final_answer"])
```

## 🏗️ Architecture Overview

### Core Components

```
RA9 Cognitive Architecture
├── Core Engine (ra9/core/)
│   ├── engine.py              # Main cognitive orchestrator
│   ├── schemas.py             # Data structures and types
│   ├── gating_manager.py      # Quality gates and quarantine
│   ├── agent_critique.py      # Self-critique system
│   ├── meta_coherence_engine.py # Conflict resolution
│   ├── neuromodulation_controller.py # Attention control
│   └── memory_manager.py      # Persistent memory
├── Agents (ra9/agents/)
│   ├── logic_agent.py         # Logical reasoning
│   ├── emotion_agent.py       # Emotional processing
│   ├── creative_agent.py      # Creative generation
│   ├── strategy_agent.py      # Strategic planning
│   └── meta_coherence_agent.py # Meta-cognitive oversight
├── Tools (ra9/tools/)
│   ├── search_agent.py        # Web search capabilities
│   └── tool_api.py           # Tool integration
└── Memory (ra9/memory/)
    └── memory_manager.py      # Episodic and semantic memory
```

### Cognitive Flow

1. **Input Processing**: Query classification and complexity analysis
2. **Agent Dispatch**: Route to appropriate specialized agents
3. **Local Processing**: Each agent generates responses with confidence scores
4. **Quality Gates**: Self-critique and validation before broadcast
5. **Global Workspace**: Centralized information sharing and conflict resolution
6. **Meta-Coherence**: Cross-agent validation and conflict resolution
7. **Memory Integration**: Store results in episodic and semantic memory
8. **Output Generation**: Synthesize final response

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional
RA9_LOG_LEVEL=INFO
RA9_MEMORY_PATH=./memory
RA9_MAX_ITERATIONS=5
```

### Configuration Files

- `ra9/core/config.py`: System-wide configuration parameters
- `ra9/core/self_persona.yaml`: RA9's personality and behavior settings

### Quality Control Settings

```python
# In ra9/core/config.py
CRITIC_MAX_ALLOWED_ISSUES = 0      # Strict quality control
COHERENCE_THRESHOLD = 0.85         # High coherence requirement
```

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=ra9

# Run specific test categories
pytest tests/test_quality_guards.py
pytest tests/test_integration_quality.py
```

### Test Categories

- **Quality Guards**: Confidence consistency, gating behavior
- **Integration Tests**: End-to-end workflow validation
- **Agent Tests**: Individual agent functionality
- **Memory Tests**: Persistent storage validation

## 📊 Quality Metrics

RA9 includes comprehensive quality monitoring:

```python
from ra9.core.cli_quality_summary import run_quality_summary

# Get quality metrics
metrics = run_quality_summary()
print(f"Broadcast Count: {metrics['broadcast_count']}")
print(f"Quarantine Count: {metrics['quarantine_count']}")
print(f"Coherence Score: {metrics['coherence']}")
print(f"Critique Pass Rate: {metrics['critique_pass_rate']}")
```

## 🔍 Debugging and Monitoring

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Access Quarantine Items

```python
from ra9.test_complete_brain_architecture import test_complete_brain_workflow

result = test_complete_brain_workflow("test query")
quarantine = result.get("quarantine", [])
for item in quarantine:
    print(f"Quarantined: {item['reason']}")
```

### Trace Analysis

```python
# Get detailed iteration trace
result = test_complete_brain_workflow("complex query")
trace = result.get("iteration_trace", [])

for iteration in trace:
    print(f"Iteration {iteration['iteration']}:")
    print(f"  Agents: {len(iteration.get('agentOutputs', []))}")
    print(f"  Critiques: {len(iteration.get('criticReports', []))}")
    print(f"  Coherence: {iteration.get('coherence', {}).get('coherence_score', 'N/A')}")
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   Error: GEMINI_API_KEY not set
   Solution: Add your API key to .env file
   ```

2. **Import Errors**
   ```
   Error: ModuleNotFoundError
   Solution: Ensure virtual environment is activated and dependencies installed
   ```

3. **Memory Permission Issues**
   ```
   Error: Permission denied writing to memory/
   Solution: Check file permissions or change RA9_MEMORY_PATH
   ```

4. **Quality Gate Failures**
   ```
   Issue: All items quarantined
   Solution: Check CRITIC_MAX_ALLOWED_ISSUES setting or improve agent prompts
   ```

### Performance Optimization

- **Memory Management**: Regularly clean up old memory files
- **Batch Processing**: Use appropriate `loopDepth` for query complexity
- **Resource Monitoring**: Monitor CPU and memory usage during processing

## 📚 Advanced Usage

### Custom Agent Development

```python
from ra9.agents.logic_agent import LogicAgent
from ra9.core.schemas import AgentOutput, AgentType

class CustomAgent(LogicAgent):
    def process_query(self, query, persona):
        # Your custom logic here
        return AgentOutput(
            agent=AgentType.LOGICAL,
            text_draft="Custom response",
            reasoning_trace=["Step 1", "Step 2"],
            confidence=0.8,
            confidence_rationale="Based on custom analysis"
        )
```

### Memory Integration

```python
from ra9.memory.memory_manager import store_memory, retrieve_memory

# Store important information
store_memory("user_preference", "Prefers detailed explanations", "user123")

# Retrieve context
context = retrieve_memory("user123")
```

### Custom Quality Gates

```python
from ra9.core.gating_manager import GateEngine, GatingPolicy

class CustomGatingPolicy(GatingPolicy):
    def should_gate(self, candidate, context):
        # Your custom gating logic
        return candidate.confidence > 0.7
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Make your changes
5. Run tests: `pytest`
6. Commit changes: `git commit -m "Add amazing feature"`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all public functions
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Global Workspace Theory and cognitive architectures
- Built with LangChain and modern AI frameworks
- Community contributions and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/LevelSUB-zero/rA9-Base/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LevelSUB-zero/rA9-Base/discussions)
- **Documentation**: [Project Wiki](https://github.com/LevelSUB-zero/rA9-Base/wiki)

---

**RA9 Development Team** - Building the future of cognitive AI