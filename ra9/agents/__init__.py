"""
RA9 Cognitive Agents.

This module contains all the specialized cognitive agents.
"""

from .base_agent import BaseAgent, AgentResult
from .logic_agent import LogicAgent
from .emotion_agent import EmotionAgent
from .creative_agent import CreativeAgent
from .strategy_agent import StrategicAgent
from .meta_coherence_agent import MetaCoherenceAgent
from .feedback_agent import FeedbackAgent

__all__ = [
    "BaseAgent",
    "AgentResult", 
    "LogicAgent",
    "EmotionAgent",
    "CreativeAgent",
    "StrategicAgent",
    "MetaCoherenceAgent",
    "FeedbackAgent",
]
