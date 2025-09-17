"""
RA9 Core Data Schemas - Brain-like Architecture
Implements the computational analogues of brain structures
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json


class ModalityType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    CODE = "code"
    MULTIMODAL = "multimodal"


class AgentType(Enum):
    LOGICAL = "logical"
    EMOTIONAL = "emotional"
    CREATIVE = "creative"
    STRATEGIC = "strategic"
    VERIFIER = "verifier"
    ARBITER = "arbiter"


@dataclass
class Percept:
    """Sensory input representation - analogous to thalamic relay"""
    modality: ModalityType
    embedding: List[float]
    tokens: List[str]
    raw_text: str
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    user_id: str = ""
    privacy_flags: Dict[str, bool] = field(default_factory=dict)


@dataclass
class AgentOutput:
    """Output from Local Reasoners (cortical columns)"""
    agent: AgentType
    text_draft: str
    reasoning_trace: List[str]
    confidence: float
    confidence_rationale: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    memory_hits: List[Dict[str, Any]] = field(default_factory=list)
    iteration: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentCritique:
    """Self-critique results from Agent Mini-Critique"""
    agent: AgentType
    passed: bool
    issues: List[str] = field(default_factory=list)
    suggested_edits: List[str] = field(default_factory=list)
    confidence_impact: float = 0.0
    escalate: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConflictTicket:
    """Meta-coherence conflict resolution"""
    conflict_id: str
    conflicting_agents: List[AgentType]
    conflict_type: str  # "contradiction", "inconsistency", "missing_evidence"
    description: str
    severity: float  # 0.0 to 1.0
    suggested_resolution: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BroadcastItem:
    """Global Workspace broadcast content"""
    id: str
    text: str
    contributors: List[AgentType]
    confidence: float
    speculative: bool = False
    iteration: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActiveRepresentation:
    """Working Memory slot content"""
    content: str
    source_agents: List[AgentType]
    timestamp: datetime = field(default_factory=datetime.now)
    decay: float = 1.0  # Decay factor over time
    priority: float = 0.5  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NeuromodulatorState:
    """Neuromodulation control signals"""
    attention_gain: float = 1.0  # ACh analog
    explore_noise: float = 0.2   # NE analog  
    reward_signal: float = 0.0   # DA analog
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IterationTrace:
    """Complete trace of reasoning iterations"""
    job_id: str
    iterations: List[Dict[str, Any]] = field(default_factory=list)
    final_confidence: float = 0.0
    coherence_score: float = 0.0
    total_iterations: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VerifierResult:
    """Global verifier output"""
    job_id: str
    passed: bool
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    issues: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QueryRequest:
    """Client request schema"""
    job_id: str
    session_id: str = ""
    user_id: str = ""
    text: str = ""
    mode: str = "concise"  # concise|deep|debate|planner
    loop_depth: int = 2
    allow_memory_write: bool = False
    privacy_flags: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextBundle:
    """Preprocessed context for agents"""
    percept: Percept
    memories: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    label_confidences: List[float] = field(default_factory=list)
    reasoning_depth: str = "shallow"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaSelfReport:
    """Meta-cognitive self-report"""
    job_id: str
    agents_run: List[AgentType]
    iterations: int
    coherence_ok: bool
    confidence_estimate: float
    conflicts_resolved: int = 0
    next_steps: List[str] = field(default_factory=list)
    reasoning_path: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


def serialize_dataclass(obj) -> str:
    """Serialize dataclass to JSON string"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(obj, default=json_serializer, indent=2)


def deserialize_dataclass(data: str, target_class):
    """Deserialize JSON string to dataclass"""
    obj_data = json.loads(data)
    return target_class(**obj_data)
