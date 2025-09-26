"""
Base agent class for RA9 cognitive agents.

This module provides the base class that all cognitive agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ..core.logger import get_logger


@dataclass
class AgentResult:
    """Result from an agent processing."""
    
    answer: str
    quality_score: float
    confidence: float
    reasoning: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    citations: Optional[List[str]] = None
    learning_improvements: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "metadata": self.metadata or {},
            "citations": self.citations or [],
            "learning_improvements": self.learning_improvements or [],
        }


class BaseAgent(ABC):
    """Base class for all RA9 cognitive agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"ra9.agents.{name.lower()}")
        self._initialized = False
    
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any]) -> AgentResult:
        """
        Process a query and return a result.
        
        Args:
            query: The query to process
            context: Additional context including persona, memory, etc.
            
        Returns:
            AgentResult with the processed response
        """
        pass
    
    def initialize(self) -> None:
        """Initialize the agent (called once before first use)."""
        if not self._initialized:
            self._setup()
            self._initialized = True
            self.logger.info(f"Agent {self.name} initialized")
    
    def _setup(self) -> None:
        """Setup method for agent-specific initialization."""
        pass
    
    def validate_input(self, query: str, context: Dict[str, Any]) -> bool:
        """Validate input before processing."""
        if not query or not query.strip():
            self.logger.warning("Empty query received")
            return False
        return True
    
    def preprocess(self, query: str, context: Dict[str, Any]) -> str:
        """Preprocess query before main processing."""
        return query.strip()
    
    def postprocess(self, result: AgentResult, query: str, context: Dict[str, Any]) -> AgentResult:
        """Postprocess result after main processing."""
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "description": self.description,
            "initialized": self._initialized,
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
