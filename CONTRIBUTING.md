# Contributing to RA9

Thank you for your interest in contributing to RA9! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project follows a code of conduct that we expect all contributors to adhere to:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of AI/ML concepts
- Familiarity with multi-agent systems (helpful but not required)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/rA9-Base.git
   cd rA9-Base
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv ra9_dev_env
   
   # Activate (Windows)
   ra9_dev_env\Scripts\activate
   
   # Activate (macOS/Linux)
   source ra9_dev_env/bin/activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys
   # Add your GEMINI_API_KEY
   ```

4. **Run tests to verify setup**
   ```bash
   python examples/test_runner.py
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix issues and improve stability
- **Feature Additions**: Add new capabilities and agents
- **Performance Improvements**: Optimize existing code
- **Documentation**: Improve guides, examples, and API docs
- **Tests**: Add test coverage and quality assurance
- **Examples**: Create usage examples and tutorials

### Contribution Process

1. **Check existing issues and PRs**
   - Look for existing work on your topic
   - Comment on relevant issues to express interest

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest tests/test_your_feature.py
   
   # Run quality checks
   python examples/test_runner.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create Pull Request on GitHub
   ```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 100 characters (not 79)
- **Imports**: Use absolute imports, group by standard library, third-party, local
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Example Code Style

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExampleClass:
    """Example class demonstrating code style.
    
    This class shows the expected formatting, type hints,
    and documentation style for RA9 contributions.
    
    Args:
        name: The name of the example
        value: A numeric value
        metadata: Optional additional data
    """
    name: str
    value: float
    metadata: Optional[Dict[str, Any]] = None
    
    def process_data(self, input_data: List[str]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: List of input strings to process
            
        Returns:
            Dictionary containing processed results
            
        Raises:
            ValueError: If input_data is empty
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        # Process the data
        results = {}
        for item in input_data:
            results[item] = self._process_item(item)
        
        return results
    
    def _process_item(self, item: str) -> str:
        """Private method to process individual items."""
        return item.upper()
```

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Third-party imports
import numpy as np
import pandas as pd
from langchain import LLMChain

# Local imports
from ra9.core.schemas import AgentOutput
from ra9.agents.base_agent import BaseAgent
```

## Testing

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Quality Tests**: Test quality gates and validation
- **End-to-End Tests**: Test complete workflows

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from ra9.core.schemas import AgentOutput, AgentType

class TestExampleClass:
    """Test suite for ExampleClass."""
    
    def test_process_data_success(self):
        """Test successful data processing."""
        # Arrange
        example = ExampleClass("test", 1.0)
        input_data = ["item1", "item2"]
        
        # Act
        result = example.process_data(input_data)
        
        # Assert
        assert len(result) == 2
        assert result["item1"] == "ITEM1"
        assert result["item2"] == "ITEM2"
    
    def test_process_data_empty_input(self):
        """Test error handling for empty input."""
        # Arrange
        example = ExampleClass("test", 1.0)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Input data cannot be empty"):
            example.process_data([])
    
    @patch('ra9.core.engine.CognitiveEngine')
    def test_with_mock(self, mock_engine):
        """Test using mocks for external dependencies."""
        # Arrange
        mock_engine.return_value.process.return_value = "mocked result"
        
        # Act
        result = some_function_using_engine()
        
        # Assert
        assert result == "mocked result"
        mock_engine.return_value.process.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ra9

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions and classes need docstrings
- **Type Hints**: Use type hints for better IDE support and documentation
- **Comments**: Explain complex logic and non-obvious decisions
- **README Updates**: Update README.md for new features

### Documentation Style

```python
def complex_function(
    input_data: List[Dict[str, Any]], 
    threshold: float = 0.5,
    enable_validation: bool = True
) -> Dict[str, Any]:
    """Process complex data with validation and thresholding.
    
    This function performs complex data processing with multiple
    validation steps and configurable thresholds.
    
    Args:
        input_data: List of dictionaries containing input data.
            Each dict must have 'value' and 'type' keys.
        threshold: Minimum confidence threshold for processing.
            Must be between 0.0 and 1.0. Defaults to 0.5.
        enable_validation: Whether to perform input validation.
            Disable only for performance-critical scenarios.
            
    Returns:
        Dictionary containing:
            - 'processed_items': List of successfully processed items
            - 'failed_items': List of items that failed processing
            - 'confidence_scores': List of confidence scores
            - 'metadata': Additional processing metadata
            
    Raises:
        ValueError: If input_data is empty or threshold is invalid
        TypeError: If input_data contains invalid types
        
    Example:
        >>> data = [{'value': 0.8, 'type': 'test'}]
        >>> result = complex_function(data, threshold=0.7)
        >>> print(result['processed_items'])
        [{'value': 0.8, 'type': 'test'}]
    """
    # Implementation here
    pass
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest
   python examples/test_runner.py
   ```

2. **Check code style**
   ```bash
   black --check ra9/
   flake8 ra9/
   mypy ra9/
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add docstrings for new functions
   - Update examples if applicable

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Integration tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automated Checks**: CI/CD will run tests and style checks
2. **Code Review**: At least one maintainer will review
3. **Testing**: Reviewer may test changes locally
4. **Approval**: Changes approved and merged

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** for similar problems
2. **Check documentation** for solutions
3. **Try latest version** to ensure issue still exists

### Issue Template

```markdown
## Bug Report / Feature Request

### Description
Clear description of the issue or feature request

### Steps to Reproduce (for bugs)
1. Step one
2. Step two
3. Step three

### Expected Behavior
What you expected to happen

### Actual Behavior
What actually happened

### Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- RA9 Version: [e.g., 0.1.0]
- Dependencies: [e.g., langchain==0.3.27]

### Additional Context
Any other relevant information, logs, screenshots, etc.
```

## Development Tips

### Debugging

```python
# Use rich for better debugging output
from rich.console import Console
from rich.traceback import install

install()  # Better tracebacks
console = Console()

# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use ipdb for interactive debugging
import ipdb; ipdb.set_trace()
```

### Performance Profiling

```python
# Use memory profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code here
    pass

# Use line profiler
from line_profiler import LineProfiler

profiler = LineProfiler()
profiler.add_function(your_function)
profiler.enable()
# Run your code
profiler.disable()
profiler.print_stats()
```

### Common Patterns

```python
# Error handling
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise CustomException("User-friendly message") from e

# Configuration management
from ra9.core.config import get_config

config = get_config()
threshold = config.get('COHERENCE_THRESHOLD', 0.85)

# Async operations (if needed)
import asyncio

async def async_operation():
    # Async code here
    pass
```

## Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check README.md and ARCHITECTURE.md
- **Examples**: Look at examples/ directory for usage patterns

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to RA9! 🧠✨
