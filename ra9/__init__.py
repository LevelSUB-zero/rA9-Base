"""
RA9 - Ultra-Deep Cognitive Engine

A multi-agent cognitive architecture for advanced AI reasoning and problem-solving.
"""

__version__ = "0.1.0"
__author__ = "RA9 Development Team"
__email__ = "contact@ra9.ai"
__description__ = "Ultra-Deep Cognitive Engine with Multi-Agent Architecture"

# Core imports
from .core.engine import run_ra9_cognitive_engine
from .core.config import get_config, Config
from .core.logger import get_logger

# Public API
__all__ = [
    "run_ra9_cognitive_engine",
    "get_config", 
    "Config",
    "get_logger",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]