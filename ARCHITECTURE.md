# RA9 Cognitive Architecture Documentation

## Overview

RA9 implements a sophisticated multi-agent cognitive architecture inspired by brain-like processing. The system consists of specialized agents that work together through a global workspace, with quality gates, self-critique mechanisms, and meta-coherence validation.

## Core Architecture Principles

### 1. Multi-Agent Specialization
Each agent has a specific cognitive function:
- **Logical Agent**: Factual reasoning, analysis, and verification
- **Emotional Agent**: Emotional intelligence and empathy
- **Creative Agent**: Creative generation and novel solutions
- **Strategic Agent**: Long-term planning and decision-making
- **Meta-Coherence Agent**: Cross-agent validation and conflict resolution

### 2. Global Workspace Theory
Information flows through a centralized workspace where:
- Agents broadcast their outputs
- Quality gates filter content before broadcast
- Meta-coherence engine resolves conflicts
- Final synthesis occurs in working memory

### 3. Quality Assurance Pipeline
- **Self-Critique**: Each agent output is self-evaluated
- **Quality Gates**: Only validated content reaches the global workspace
- **Quarantine System**: Failed outputs are isolated for analysis
- **Rewrite Cycles**: Automatic improvement attempts with escalation

## Detailed Component Architecture

### Core Engine (`ra9/core/`)

#### `engine.py` - Main Cognitive Orchestrator
```python
class CognitiveEngine:
    """
    Central orchestrator that manages the entire cognitive workflow:
    1. Query analysis and classification
    2. Agent dispatch and coordination
    3. Quality gate enforcement
    4. Global workspace management
    5. Meta-coherence validation
    6. Memory integration
    7. Final synthesis
    """
```

**Key Methods:**
- `process_query()`: Main entry point for query processing
- `dispatch_to_agents()`: Route queries to appropriate agents
- `validate_outputs()`: Quality gate enforcement
- `synthesize_response()`: Final response generation

#### `schemas.py` - Data Structures
Defines the core data types used throughout the system:

```python
@dataclass
class AgentOutput:
    """Output from Local Reasoners (cortical columns)"""
    agent: AgentType
    text_draft: str
    reasoning_trace: List[str]
    confidence: float
    confidence_rationale: str
    citations: List[Dict[str, Any]]
    memory_hits: List[Dict[str, Any]]
    iteration: int
    timestamp: datetime

@dataclass
class BroadcastItem:
    """Global Workspace broadcast content"""
    id: str
    text: str
    contributors: List[AgentType]
    confidence: float
    speculative: bool
    metadata: Dict[str, Any]

@dataclass
class AgentCritique:
    """Self-critique results from Agent Mini-Critique"""
    agent: AgentType
    passed: bool
    issues: List[str]
    suggested_edits: List[str]
    escalate: bool
```

#### `gating_manager.py` - Quality Control System
```python
class GateEngine:
    """
    Controls what content gets into Working Memory and Global Workspace.
    Implements quality gates based on critique and verification results.
    """
    
    def evaluate_candidates(self, candidates, context):
        """
        Quality gate logic:
        - Block unless agentCritique.passed == True OR verifier.passed == True
        - Quarantine failed items for analysis
        - Track resource consumption
        """
```

**Key Features:**
- **Deterministic Gating**: Strict quality requirements
- **Adaptive Gating**: Dynamic thresholds based on context
- **Quarantine System**: Isolate failed outputs
- **Resource Tracking**: Monitor computational costs

#### `agent_critique.py` - Self-Evaluation System
```python
class AgentCritiqueManager:
    """
    Manages self-critique and rewrite cycles:
    1. Structured critique using LLM
    2. Automatic rewrite attempts
    3. Escalation for persistent failures
    """
    
    def critique_agent_output(self, output):
        """
        Critique process:
        1. Generate structured critique (pass, issues, suggested_edits)
        2. If failed, attempt one rewrite
        3. If still failed, escalate to arbiter
        """
```

**Critique Criteria:**
- Factual accuracy
- Internal consistency
- Unsupported claims
- Hallucination risk
- Format compliance
- Brevity and clarity

#### `meta_coherence_engine.py` - Conflict Resolution
```python
class MetaCoherenceEngine:
    """
    Detects and resolves conflicts between agent outputs:
    1. Conflict detection across agents
    2. Coherence scoring
    3. Resolution strategies
    4. Final synthesis validation
    """
    
    def analyze_coherence(self, agent_outputs):
        """
        Coherence analysis:
        1. Detect contradictions between agents
        2. Calculate overall coherence score
        3. Generate resolution strategies
        4. Determine if synthesis is ready
        """
```

#### `neuromodulation_controller.py` - Attention Control
```python
class NeuromodulationController:
    """
    Manages global scalar modulators:
    - Attention: Focus and precision control
    - Exploration: Creativity and novelty
    - Reward: Motivation and goal alignment
    """
    
    def modulate_agent_behavior(self, agent_type, base_confidence, base_temperature):
        """
        Modulate agent parameters based on global state:
        - Attention gain affects confidence thresholds
        - Exploration affects temperature and creativity
        - Reward affects motivation and persistence
        """
```

### Agent System (`ra9/agents/`)

#### Agent Base Class
All agents inherit from a common base class that provides:
- Standardized input/output interfaces
- Confidence scoring mechanisms
- Reasoning trace generation
- Memory integration hooks

#### Specialized Agents

**Logical Agent (`logic_agent.py`)**
- Factual reasoning and analysis
- Evidence-based conclusions
- Citation and source tracking
- High precision, low creativity

**Emotional Agent (`emotion_agent.py`)**
- Emotional intelligence and empathy
- Social and interpersonal understanding
- Emotional context awareness
- Balanced precision and empathy

**Creative Agent (`creative_agent.py`)**
- Novel idea generation
- Creative problem solving
- High creativity, variable precision
- Divergent thinking patterns

**Strategic Agent (`strategy_agent.py`)**
- Long-term planning and decision-making
- Risk assessment and mitigation
- Resource allocation
- Goal-oriented thinking

**Meta-Coherence Agent (`meta_coherence_agent.py`)**
- Cross-agent validation
- Conflict detection and resolution
- Meta-cognitive oversight
- System-level quality control

### Memory System (`ra9/memory/`)

#### `memory_manager.py` - Persistent Memory
```python
class MemoryManager:
    """
    Manages both episodic and semantic memory:
    - Episodic: Specific experiences and interactions
    - Semantic: General knowledge and concepts
    - Vector storage for similarity search
    - Context-aware retrieval
    """
```

**Memory Types:**
- **Episodic Memory**: User interactions, specific conversations
- **Semantic Memory**: General knowledge, learned concepts
- **Working Memory**: Current session context
- **Long-term Memory**: Persistent knowledge base

### Quality Assurance Pipeline

#### 1. Input Validation
- Query classification and complexity analysis
- Input sanitization and preprocessing
- Context preparation and memory retrieval

#### 2. Agent Processing
- Specialized agent execution
- Confidence scoring and rationale
- Reasoning trace generation
- Citation and evidence tracking

#### 3. Self-Critique
- Structured critique generation
- Issue identification and categorization
- Suggested edits and improvements
- Pass/fail determination

#### 4. Quality Gates
- Critique validation
- Verification checks (when available)
- Confidence thresholds
- Quarantine for failed outputs

#### 5. Global Workspace
- Centralized information sharing
- Conflict detection and resolution
- Meta-coherence validation
- Synthesis preparation

#### 6. Final Synthesis
- Multi-agent output integration
- Conflict resolution
- Coherence validation
- Final response generation

#### 7. Memory Integration
- Store successful outputs
- Update knowledge base
- Track user preferences
- Maintain context continuity

## Configuration and Tuning

### System Parameters (`ra9/core/config.py`)

```python
# Quality Control
CRITIC_MAX_ALLOWED_ISSUES = 0      # Strict quality control
COHERENCE_THRESHOLD = 0.85         # High coherence requirement

# Performance
MAX_ITERATIONS = 5                  # Maximum processing iterations
MEMORY_CACHE_SIZE = 1000           # Memory cache size
RESOURCE_LIMITS = {                # Resource consumption limits
    "max_tokens": 10000,
    "max_processing_time": 300
}

# Neuromodulation
ATTENTION_GAIN = 1.0               # Attention modulation factor
EXPLORATION_FACTOR = 1.0           # Creativity modulation factor
REWARD_SIGNAL = 1.0                # Motivation modulation factor
```

### Agent-Specific Tuning

Each agent can be tuned through:
- **Temperature**: Controls randomness and creativity
- **Confidence Thresholds**: Minimum confidence for output
- **Memory Integration**: How much context to use
- **Citation Requirements**: Evidence standards

## Performance Characteristics

### Scalability
- **Horizontal**: Add more specialized agents
- **Vertical**: Increase processing depth and iterations
- **Memory**: Expand knowledge base and context

### Quality Metrics
- **Critique Pass Rate**: Percentage of outputs passing self-critique
- **Coherence Score**: Internal consistency across agents
- **Broadcast Success Rate**: Percentage of outputs reaching global workspace
- **Quarantine Rate**: Percentage of outputs requiring isolation

### Resource Usage
- **CPU**: Multi-agent parallel processing
- **Memory**: Vector storage and context management
- **API Calls**: LLM usage for agents and critique
- **Storage**: Persistent memory and knowledge base

## Extension Points

### Adding New Agents
1. Inherit from base agent class
2. Implement specialized processing logic
3. Define confidence scoring criteria
4. Add to agent registry
5. Update dispatch logic

### Custom Quality Gates
1. Implement custom gating policy
2. Define evaluation criteria
3. Add to gate engine
4. Configure thresholds

### Memory Extensions
1. Implement custom memory types
2. Add retrieval strategies
3. Define storage formats
4. Integrate with memory manager

## Debugging and Monitoring

### Logging Levels
- **DEBUG**: Detailed processing traces
- **INFO**: General processing information
- **WARNING**: Quality issues and fallbacks
- **ERROR**: Critical failures and exceptions

### Trace Information
- **Agent Outputs**: All agent responses with metadata
- **Critique Reports**: Self-evaluation results
- **Coherence Analysis**: Conflict detection and resolution
- **Quality Metrics**: Performance and quality statistics

### Quarantine Analysis
- **Failed Outputs**: Items that didn't pass quality gates
- **Failure Reasons**: Specific issues identified
- **Escalation Status**: Items requiring human review
- **Improvement Suggestions**: Potential fixes and optimizations

This architecture provides a robust, scalable foundation for advanced cognitive AI systems while maintaining quality, coherence, and reliability.
