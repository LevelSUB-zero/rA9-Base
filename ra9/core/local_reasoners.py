"""
Local Reasoners - Cortical columns / recurrent microcircuits analogue
Small specialized models that produce candidate "micro-answers"
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .schemas import AgentOutput, AgentType, ContextBundle, Percept
from . import validators
from ..tools.tool_api import ask_gemini


class LocalReasoner:
    """Base class for local reasoners (cortical columns)"""
    
    def __init__(self, agent_type: AgentType, role: str, prompt_template: str):
        self.agent_type = agent_type
        self.role = role
        self.prompt_template = prompt_template
        self.confidence_threshold = 0.3
        self.max_reasoning_steps = 5
    
    def run(self, context: ContextBundle, neuromodulation_params: Dict[str, float] = None) -> AgentOutput:
        """
        Run the local reasoner on the given context
        
        Args:
            context: Preprocessed context bundle
            neuromodulation_params: Neuromodulator-modulated parameters
            
        Returns:
            AgentOutput with reasoning trace and confidence
        """
        if neuromodulation_params is None:
            neuromodulation_params = {}
        
        # Build prompt with context
        prompt = self._build_prompt(context, neuromodulation_params)
        
        # Generate response
        response = ask_gemini(prompt)
        
        # Extract reasoning trace
        reasoning_trace = self._extract_reasoning_trace(response)
        
        # Calculate confidence
        confidence = self._calculate_confidence(response, reasoning_trace, neuromodulation_params)
        
        # Extract citations and memory hits
        citations = self._extract_citations(response)
        memory_hits = self._extract_memory_hits(response, context)
        
        agent_output = AgentOutput(
            agent=self.agent_type,
            text_draft=response,
            reasoning_trace=reasoning_trace,
            confidence=confidence,
            confidence_rationale=self._build_confidence_rationale(response, reasoning_trace, neuromodulation_params),
            citations=citations,
            memory_hits=memory_hits,
            iteration=0,
            timestamp=datetime.now()
        )
        # Enforce schema/policy constraints and sanitize if needed
        agent_output = validators.validate_agent_output(agent_output)
        return agent_output
    
    def _build_prompt(self, context: ContextBundle, neuromodulation_params: Dict[str, float]) -> str:
        """Build the prompt for this reasoner"""
        # Apply neuromodulation to prompt
        temperature = neuromodulation_params.get('temperature', 0.7)
        confidence_boost = neuromodulation_params.get('confidence', 1.0)
        
        prompt = f"""
{self.prompt_template}

Role: {self.role}
Query: {context.percept.raw_text}

Context:
- Modality: {context.percept.modality.value}
- Reasoning Depth: {context.reasoning_depth}
- Labels: {', '.join(context.labels)}
- Memory Context: {self._format_memory_context(context.memories)}

Instructions:
- Provide a clear, focused response from your {self.role} perspective
- Show your reasoning steps clearly
- Be confident but acknowledge uncertainty when appropriate
- Confidence level should be: {confidence_boost:.2f}
- Temperature for creativity: {temperature:.2f}

Response:
"""
        return prompt
    
    def _extract_reasoning_trace(self, response: str) -> List[str]:
        """Extract reasoning steps from response"""
        # Simple extraction - look for numbered steps or bullet points
        lines = response.split('\n')
        reasoning_steps = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                line.startswith(('-', '*', '•')) or
                'step' in line.lower() or
                'reasoning' in line.lower()):
                reasoning_steps.append(line)
        
        # If no explicit steps found, split by sentences
        if not reasoning_steps:
            sentences = response.split('.')
            reasoning_steps = [s.strip() + '.' for s in sentences if s.strip()][:self.max_reasoning_steps]
        
        return reasoning_steps[:self.max_reasoning_steps]
    
    def _calculate_confidence(self, response: str, reasoning_trace: List[str], 
                            neuromodulation_params: Dict[str, float]) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.5
        
        # Length factor - longer responses often more confident
        length_factor = min(len(response) / 500.0, 1.0)
        
        # Reasoning trace factor
        trace_factor = min(len(reasoning_trace) / 3.0, 1.0)
        
        # Uncertainty indicators
        uncertainty_words = ['maybe', 'perhaps', 'might', 'could', 'unclear', 'not sure', 'possibly']
        uncertainty_count = sum(1 for word in uncertainty_words if word.lower() in response.lower())
        uncertainty_factor = max(0.0, 1.0 - (uncertainty_count * 0.1))
        
        # Confidence indicators
        confidence_words = ['definitely', 'certainly', 'sure', 'clearly', 'obviously', 'confident']
        confidence_count = sum(1 for word in confidence_words if word.lower() in response.lower())
        confidence_factor = min(1.0, 1.0 + (confidence_count * 0.05))
        
        # Calculate final confidence
        final_confidence = (base_confidence + length_factor + trace_factor + 
                          uncertainty_factor + confidence_factor) / 5.0
        
        # Apply neuromodulation
        neuromod_confidence = neuromodulation_params.get('confidence', 1.0)
        final_confidence *= neuromod_confidence
        
        return max(0.0, min(1.0, final_confidence))

    def _build_confidence_rationale(self, response: str, reasoning_trace: List[str], neuromodulation_params: Dict[str, float]) -> str:
        """Generate a concise rationale for the numeric confidence."""
        reasons = []
        if reasoning_trace:
            reasons.append(f"{len(reasoning_trace)} reasoning steps")
        if neuromodulation_params.get('attention_factor'):
            reasons.append("heightened attention")
        if neuromodulation_params.get('explore_factor') and neuromodulation_params.get('explore_factor') > 1.0:
            reasons.append("some exploration")
        if not reasons:
            reasons.append("balanced assessment")
        return ", ".join(reasons) + "."
    
    def _extract_citations(self, response: str) -> List[Dict[str, Any]]:
        """Extract citations from response"""
        citations = []
        
        # Look for citation patterns
        import re
        citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(([^)]+)\)',  # (source), (reference)
            r'according to ([^,\.]+)',
            r'as stated in ([^,\.]+)',
            r'research shows ([^,\.]+)'
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                citations.append({
                    'source': match,
                    'score': 0.8,  # Default confidence
                    'type': 'text_reference'
                })
        
        return citations[:5]  # Limit to 5 citations
    
    def _extract_memory_hits(self, response: str, context: ContextBundle) -> List[Dict[str, Any]]:
        """Extract memory hits from context"""
        memory_hits = []
        
        # Check if response references context memories
        for memory_type, memories in context.memories.items():
            for memory in memories:
                # Simple keyword matching
                memory_text = str(memory).lower()
                response_lower = response.lower()
                
                # Check for overlap
                memory_words = set(memory_text.split())
                response_words = set(response_lower.split())
                overlap = len(memory_words.intersection(response_words))
                
                if overlap > 2:  # Significant overlap
                    memory_hits.append({
                        'id': memory.get('id', 'unknown'),
                        'score': min(overlap / 10.0, 1.0),
                        'type': memory_type,
                        'content': memory_text[:100] + '...' if len(memory_text) > 100 else memory_text
                    })
        
        return memory_hits[:5]  # Limit to 5 memory hits
    
    def _format_memory_context(self, memories: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format memory context for prompt"""
        if not memories:
            return "No relevant memories found."
        
        context_parts = []
        for memory_type, memory_list in memories.items():
            if memory_list:
                context_parts.append(f"{memory_type.title()}: {len(memory_list)} items")
        
        return "; ".join(context_parts) if context_parts else "No relevant memories found."


class LogicalReasoner(LocalReasoner):
    """Logical reasoning agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.LOGICAL,
            role="Logical Analysis Expert",
            prompt_template="""
You are a logical reasoning expert. Your role is to provide systematic, evidence-based analysis.

Focus on:
- Step-by-step logical reasoning
- Evidence evaluation and validation
- Identifying assumptions and implications
- Structured problem-solving approaches
- Factual accuracy and consistency

Provide clear, methodical analysis with logical flow.
"""
        )


class EmotionalReasoner(LocalReasoner):
    """Emotional reasoning agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.EMOTIONAL,
            role="Emotional Intelligence Specialist",
            prompt_template="""
You are an emotional intelligence specialist. Your role is to understand and address emotional aspects.

Focus on:
- Emotional context and human impact
- Empathy and perspective-taking
- Emotional regulation strategies
- Interpersonal dynamics
- Psychological well-being considerations

Provide emotionally intelligent, empathetic responses.
"""
        )


class CreativeReasoner(LocalReasoner):
    """Creative reasoning agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CREATIVE,
            role="Creative Innovation Expert",
            prompt_template="""
You are a creative innovation expert. Your role is to generate novel, imaginative solutions.

Focus on:
- Out-of-the-box thinking and innovation
- Creative problem-solving techniques
- Artistic and aesthetic considerations
- Metaphorical and analogical reasoning
- Brainstorming and ideation

Provide creative, innovative, and inspiring responses.
"""
        )


class StrategicReasoner(LocalReasoner):
    """Strategic reasoning agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.STRATEGIC,
            role="Strategic Planning Specialist",
            prompt_template="""
You are a strategic planning specialist. Your role is to provide long-term, strategic thinking.

Focus on:
- Long-term planning and vision
- Resource allocation and optimization
- Risk assessment and mitigation
- Competitive analysis and positioning
- Goal setting and milestone planning

Provide strategic, forward-thinking responses.
"""
        )


class VerifierReasoner(LocalReasoner):
    """Verification and fact-checking agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.VERIFIER,
            role="Fact-Checking and Verification Expert",
            prompt_template="""
You are a fact-checking and verification expert. Your role is to validate claims and ensure accuracy.

Focus on:
- Fact verification and source checking
- Identifying potential misinformation
- Evidence quality assessment
- Logical consistency checking
- Credibility evaluation

Provide thorough, accurate verification with evidence.
"""
        )


class ArbiterReasoner(LocalReasoner):
    """Arbitration and conflict resolution agent"""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.ARBITER,
            role="Conflict Resolution and Arbitration Expert",
            prompt_template="""
You are a conflict resolution and arbitration expert. Your role is to resolve conflicts between different perspectives.

Focus on:
- Identifying common ground and shared interests
- Mediating between conflicting viewpoints
- Finding balanced, fair solutions
- Synthesizing different perspectives
- Building consensus and compromise

Provide balanced, fair, and constructive arbitration.
"""
        )


class LocalReasonerFactory:
    """Factory for creating local reasoners"""
    
    _reasoners = {
        AgentType.LOGICAL: LogicalReasoner,
        AgentType.EMOTIONAL: EmotionalReasoner,
        AgentType.CREATIVE: CreativeReasoner,
        AgentType.STRATEGIC: StrategicReasoner,
        AgentType.VERIFIER: VerifierReasoner,
        AgentType.ARBITER: ArbiterReasoner
    }
    
    @classmethod
    def create_reasoner(cls, agent_type: AgentType) -> LocalReasoner:
        """Create a local reasoner of the specified type"""
        if agent_type not in cls._reasoners:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return cls._reasoners[agent_type]()
    
    @classmethod
    def create_reasoners(cls, agent_types: List[AgentType]) -> List[LocalReasoner]:
        """Create multiple local reasoners"""
        return [cls.create_reasoner(agent_type) for agent_type in agent_types]
    
    @classmethod
    def get_available_types(cls) -> List[AgentType]:
        """Get list of available agent types"""
        return list(cls._reasoners.keys())


class ParallelReasonerExecutor:
    """Executes multiple reasoners in parallel"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_parallel(self, reasoners: List[LocalReasoner], 
                        context: ContextBundle,
                        neuromodulation_params: Dict[str, float] = None) -> List[AgentOutput]:
        """
        Execute multiple reasoners in parallel
        
        Args:
            reasoners: List of reasoners to execute
            context: Context bundle for all reasoners
            neuromodulation_params: Neuromodulator parameters
            
        Returns:
            List of AgentOutputs from all reasoners
        """
        if neuromodulation_params is None:
            neuromodulation_params = {}
        
        # Submit all tasks
        future_to_reasoner = {
            self.executor.submit(reasoner.run, context, neuromodulation_params): reasoner
            for reasoner in reasoners
        }
        
        # Collect results
        results = []
        for future in as_completed(future_to_reasoner):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                reasoner = future_to_reasoner[future]
                print(f"Error in {reasoner.agent_type.value} reasoner: {e}")
                
                # Create error result
                error_result = AgentOutput(
                    agent=reasoner.agent_type,
                    text_draft=f"Error in {reasoner.agent_type.value} reasoning: {str(e)}",
                    reasoning_trace=[f"Error occurred: {str(e)}"],
                    confidence=0.0,
                    citations=[],
                    memory_hits=[],
                    iteration=0,
                    timestamp=datetime.now()
                )
                results.append(error_result)
        
        return results
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


def create_reasoner_suite() -> List[LocalReasoner]:
    """Create a complete suite of reasoners"""
    factory = LocalReasonerFactory()
    return factory.create_reasoners(factory.get_available_types())


def execute_reasoner_suite(context: ContextBundle, 
                          selected_types: List[AgentType] = None,
                          neuromodulation_params: Dict[str, float] = None) -> List[AgentOutput]:
    """
    Execute a suite of reasoners on the given context
    
    Args:
        context: Context bundle
        selected_types: Specific agent types to run (None for all)
        neuromodulation_params: Neuromodulator parameters
        
    Returns:
        List of AgentOutputs
    """
    if selected_types is None:
        selected_types = LocalReasonerFactory.get_available_types()
    
    reasoners = [LocalReasonerFactory.create_reasoner(agent_type) for agent_type in selected_types]
    executor = ParallelReasonerExecutor()
    
    try:
        results = executor.execute_parallel(reasoners, context, neuromodulation_params)
        return results
    finally:
        executor.shutdown()
