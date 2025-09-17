"""
Meta-Coherence Engine - Conflict resolution and synthesis system
Implements cross-agent conflict detection and resolution
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import re

from .schemas import AgentOutput, ConflictTicket, AgentType, BroadcastItem
from .config import COHERENCE_THRESHOLD
from ..tools.tool_api import ask_gemini


class ConflictDetector:
    """Detects conflicts between agent outputs"""
    
    def __init__(self):
        self.conflict_patterns = {
            'contradiction': [
                r'(\w+)\s+(?:is|are)\s+(?:not|never|no)\s+(\w+)',
                r'(?:not|never|no)\s+(\w+)\s+(?:is|are)\s+(\w+)',
                r'(\w+)\s+(?:contradicts|opposes|conflicts with)\s+(\w+)'
            ],
            'inconsistency': [
                r'(?:however|but|although|despite)\s+',
                r'(?:on the other hand|conversely|alternatively)',
                r'(?:this contradicts|this conflicts with|this opposes)'
            ],
            'missing_evidence': [
                r'(?:no evidence|insufficient evidence|lack of evidence)',
                r'(?:unclear|unproven|speculative|assumption)',
                r'(?:cannot be verified|cannot be confirmed)'
            ]
        }
    
    def detect_conflicts(self, agent_outputs: List[AgentOutput]) -> List[ConflictTicket]:
        """
        Detect conflicts between agent outputs
        
        Args:
            agent_outputs: List of AgentOutputs to analyze
            
        Returns:
            List of ConflictTickets
        """
        conflicts = []
        
        # Compare each pair of outputs
        for i, output1 in enumerate(agent_outputs):
            for j, output2 in enumerate(agent_outputs[i+1:], i+1):
                conflict = self._compare_outputs(output1, output2)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _compare_outputs(self, output1: AgentOutput, output2: AgentOutput) -> Optional[ConflictTicket]:
        """Compare two outputs for conflicts"""
        # Skip if same agent
        if output1.agent == output2.agent:
            return None
        
        # Extract key claims from both outputs
        claims1 = self._extract_claims(output1.text_draft)
        claims2 = self._extract_claims(output2.text_draft)
        
        # Check for contradictions
        contradiction = self._find_contradiction(claims1, claims2, output1.agent, output2.agent)
        if contradiction:
            return contradiction
        
        # Check for inconsistencies
        inconsistency = self._find_inconsistency(claims1, claims2, output1.agent, output2.agent)
        if inconsistency:
            return inconsistency
        
        # Check for missing evidence
        missing_evidence = self._find_missing_evidence(output1, output2)
        if missing_evidence:
            return missing_evidence
        
        return None
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract key claims from text"""
        # Simple claim extraction - look for declarative statements
        sentences = text.split('.')
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (sentence and 
                not sentence.startswith(('?', '!')) and
                len(sentence.split()) > 3 and
                not sentence.startswith(('however', 'although', 'despite'))):
                claims.append(sentence)
        
        return claims[:5]  # Limit to 5 key claims
    
    def _find_contradiction(self, claims1: List[str], claims2: List[str], 
                          agent1: AgentType, agent2: AgentType) -> Optional[ConflictTicket]:
        """Find direct contradictions between claims"""
        for claim1 in claims1:
            for claim2 in claims2:
                if self._are_contradictory(claim1, claim2):
                    return ConflictTicket(
                        conflict_id=f"contradiction_{agent1.value}_{agent2.value}_{datetime.now().timestamp()}",
                        conflicting_agents=[agent1, agent2],
                        conflict_type="contradiction",
                        description=f"Contradiction between {agent1.value} and {agent2.value}",
                        severity=0.8,
                        suggested_resolution=f"Reconcile conflicting claims: '{claim1}' vs '{claim2}'"
                    )
        
        return None
    
    def _find_inconsistency(self, claims1: List[str], claims2: List[str],
                          agent1: AgentType, agent2: AgentType) -> Optional[ConflictTicket]:
        """Find inconsistencies between claims"""
        for claim1 in claims1:
            for claim2 in claims2:
                if self._are_inconsistent(claim1, claim2):
                    return ConflictTicket(
                        conflict_id=f"inconsistency_{agent1.value}_{agent2.value}_{datetime.now().timestamp()}",
                        conflicting_agents=[agent1, agent2],
                        conflict_type="inconsistency",
                        description=f"Inconsistency between {agent1.value} and {agent2.value}",
                        severity=0.6,
                        suggested_resolution=f"Clarify relationship between: '{claim1}' and '{claim2}'"
                    )
        
        return None
    
    def _find_missing_evidence(self, output1: AgentOutput, output2: AgentOutput) -> Optional[ConflictTicket]:
        """Find cases where evidence is missing"""
        # Check if one output has evidence and the other doesn't
        has_evidence1 = len(output1.citations) > 0 or len(output1.memory_hits) > 0
        has_evidence2 = len(output2.citations) > 0 or len(output2.memory_hits) > 0
        
        if has_evidence1 and not has_evidence2:
            return ConflictTicket(
                conflict_id=f"missing_evidence_{output2.agent.value}_{datetime.now().timestamp()}",
                conflicting_agents=[output1.agent, output2.agent],
                conflict_type="missing_evidence",
                description=f"{output2.agent.value} lacks supporting evidence",
                severity=0.4,
                suggested_resolution=f"Provide evidence for {output2.agent.value} claims"
            )
        elif has_evidence2 and not has_evidence1:
            return ConflictTicket(
                conflict_id=f"missing_evidence_{output1.agent.value}_{datetime.now().timestamp()}",
                conflicting_agents=[output1.agent, output2.agent],
                conflict_type="missing_evidence",
                description=f"{output1.agent.value} lacks supporting evidence",
                severity=0.4,
                suggested_resolution=f"Provide evidence for {output1.agent.value} claims"
            )
        
        return None
    
    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are contradictory"""
        # Simple contradiction detection
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()
        
        # Check for direct negations
        negation_pairs = [
            ('is', 'is not'), ('are', 'are not'), ('can', 'cannot'),
            ('will', 'will not'), ('should', 'should not'), ('must', 'must not')
        ]
        
        for positive, negative in negation_pairs:
            if positive in claim1_lower and negative in claim2_lower:
                return True
            if positive in claim2_lower and negative in claim1_lower:
                return True
        
        # Check for opposite keywords
        opposite_pairs = [
            ('good', 'bad'), ('right', 'wrong'), ('true', 'false'),
            ('correct', 'incorrect'), ('valid', 'invalid'), ('success', 'failure')
        ]
        
        for word1, word2 in opposite_pairs:
            if word1 in claim1_lower and word2 in claim2_lower:
                return True
            if word1 in claim2_lower and word2 in claim1_lower:
                return True
        
        return False
    
    def _are_inconsistent(self, claim1: str, claim2: str) -> bool:
        """Check if two claims are inconsistent (but not directly contradictory)"""
        # Look for inconsistency indicators
        inconsistency_indicators = [
            'however', 'but', 'although', 'despite', 'on the other hand',
            'conversely', 'alternatively', 'meanwhile', 'in contrast'
        ]
        
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()
        
        # Check if either claim contains inconsistency indicators
        for indicator in inconsistency_indicators:
            if indicator in claim1_lower or indicator in claim2_lower:
                return True
        
        return False


class ConflictResolver:
    """Resolves conflicts between agent outputs"""
    
    def __init__(self):
        self.resolution_strategies = {
            'contradiction': self._resolve_contradiction,
            'inconsistency': self._resolve_inconsistency,
            'missing_evidence': self._resolve_missing_evidence
        }
    
    def resolve_conflict(self, conflict: ConflictTicket, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """
        Resolve a conflict between agent outputs
        
        Args:
            conflict: ConflictTicket to resolve
            agent_outputs: List of all agent outputs
            
        Returns:
            Resolution result with synthesized output
        """
        strategy = self.resolution_strategies.get(conflict.conflict_type, self._resolve_generic)
        return strategy(conflict, agent_outputs)
    
    def _resolve_contradiction(self, conflict: ConflictTicket, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve contradiction conflicts"""
        conflicting_outputs = [output for output in agent_outputs 
                             if output.agent in conflict.conflicting_agents]
        
        # Use arbitration prompt to resolve contradiction
        prompt = f"""
You are an arbitration expert. Resolve the following contradiction between different perspectives.

Conflict: {conflict.description}

Conflicting outputs:
{chr(10).join(f"{output.agent.value}: {output.text_draft}" for output in conflicting_outputs)}

Resolution approach:
1. Identify the core disagreement
2. Find common ground or shared principles
3. Propose a balanced resolution that acknowledges both perspectives
4. Provide a synthesized response that addresses the contradiction

Synthesized resolution:
"""
        
        resolution = ask_gemini(prompt)
        
        return {
            'type': 'contradiction_resolution',
            'conflict_id': conflict.conflict_id,
            'resolution': resolution,
            'strategy': 'arbitration',
            'confidence': 0.7
        }
    
    def _resolve_inconsistency(self, conflict: ConflictTicket, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve inconsistency conflicts"""
        conflicting_outputs = [output for output in agent_outputs 
                             if output.agent in conflict.conflicting_agents]
        
        # Use clarification prompt to resolve inconsistency
        prompt = f"""
You are a clarification expert. Resolve the following inconsistency between different perspectives.

Inconsistency: {conflict.description}

Conflicting outputs:
{chr(10).join(f"{output.agent.value}: {output.text_draft}" for output in conflicting_outputs)}

Resolution approach:
1. Identify the specific inconsistency
2. Clarify the relationship between the perspectives
3. Show how they can coexist or complement each other
4. Provide a clear, consistent synthesis

Clarified synthesis:
"""
        
        resolution = ask_gemini(prompt)
        
        return {
            'type': 'inconsistency_resolution',
            'conflict_id': conflict.conflict_id,
            'resolution': resolution,
            'strategy': 'clarification',
            'confidence': 0.8
        }
    
    def _resolve_missing_evidence(self, conflict: ConflictTicket, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Resolve missing evidence conflicts"""
        conflicting_outputs = [output for output in agent_outputs 
                             if output.agent in conflict.conflicting_agents]
        
        # Identify which output needs evidence
        needs_evidence = None
        for output in conflicting_outputs:
            if len(output.citations) == 0 and len(output.memory_hits) == 0:
                needs_evidence = output
                break
        
        if not needs_evidence:
            return {'type': 'no_resolution_needed', 'confidence': 1.0}
        
        # Use evidence generation prompt
        prompt = f"""
You are an evidence generation expert. Help strengthen the following claim with supporting evidence.

Claim needing evidence: {needs_evidence.text_draft}
Agent: {needs_evidence.agent.value}

Evidence generation approach:
1. Identify the key claims that need support
2. Suggest specific types of evidence that would strengthen the argument
3. Provide reasoning for why this evidence would be valuable
4. Suggest how to find or generate this evidence

Evidence suggestions:
"""
        
        evidence_suggestions = ask_gemini(prompt)
        
        return {
            'type': 'evidence_resolution',
            'conflict_id': conflict.conflict_id,
            'resolution': evidence_suggestions,
            'strategy': 'evidence_generation',
            'confidence': 0.6
        }
    
    def _resolve_generic(self, conflict: ConflictTicket, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Generic conflict resolution"""
        return {
            'type': 'generic_resolution',
            'conflict_id': conflict.conflict_id,
            'resolution': f"Generic resolution for {conflict.conflict_type}",
            'strategy': 'generic',
            'confidence': 0.5
        }


class MetaCoherenceEngine:
    """Main meta-coherence engine for conflict detection and resolution"""
    
    def __init__(self):
        self.conflict_detector = ConflictDetector()
        self.conflict_resolver = ConflictResolver()
        self.coherence_history = []
    
    def analyze_coherence(self, agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
        """
        Analyze coherence of agent outputs
        
        Args:
            agent_outputs: List of AgentOutputs to analyze
            
        Returns:
            Coherence analysis result
        """
        # Detect conflicts
        conflicts = self.conflict_detector.detect_conflicts(agent_outputs)
        
        # Calculate coherence score
        coherence_score = self._calculate_coherence_score(agent_outputs, conflicts)
        
        # Resolve conflicts if any
        resolutions = []
        if conflicts:
            for conflict in conflicts:
                resolution = self.conflict_resolver.resolve_conflict(conflict, agent_outputs)
                resolutions.append(resolution)
        
        # Record analysis
        self._record_coherence_analysis(agent_outputs, conflicts, resolutions, coherence_score)
        
        return {
            'coherence_score': coherence_score,
            'conflicts': conflicts,
            'resolutions': resolutions,
            'is_coherent': coherence_score >= COHERENCE_THRESHOLD,
            'analysis_timestamp': datetime.now()
        }
    
    def _calculate_coherence_score(self, agent_outputs: List[AgentOutput], conflicts: List[ConflictTicket]) -> float:
        """Calculate overall coherence score"""
        if not agent_outputs:
            return 0.0
        
        # Base score from individual confidences
        avg_confidence = sum(output.confidence for output in agent_outputs) / len(agent_outputs)
        
        # Penalty for conflicts
        conflict_penalty = 0.0
        for conflict in conflicts:
            conflict_penalty += conflict.severity * 0.2
        
        # Bonus for evidence
        evidence_bonus = 0.0
        for output in agent_outputs:
            if output.citations or output.memory_hits:
                evidence_bonus += 0.1
        
        # Calculate final score
        coherence_score = avg_confidence - conflict_penalty + evidence_bonus
        
        return max(0.0, min(1.0, coherence_score))
    
    def _record_coherence_analysis(self, agent_outputs: List[AgentOutput], 
                                 conflicts: List[ConflictTicket],
                                 resolutions: List[Dict[str, Any]],
                                 coherence_score: float) -> None:
        """Record coherence analysis for tracking"""
        record = {
            'timestamp': datetime.now(),
            'agent_count': len(agent_outputs),
            'conflict_count': len(conflicts),
            'resolution_count': len(resolutions),
            'coherence_score': coherence_score,
            'agent_types': [output.agent.value for output in agent_outputs]
        }
        
        self.coherence_history.append(record)
        
        # Keep only recent history (last 1000 analyses)
        if len(self.coherence_history) > 1000:
            self.coherence_history = self.coherence_history[-1000:]
    
    def get_coherence_stats(self) -> Dict[str, Any]:
        """Get coherence analysis statistics"""
        if not self.coherence_history:
            return {'total_analyses': 0, 'avg_coherence': 0.0, 'conflict_rate': 0.0}
        
        total_analyses = len(self.coherence_history)
        avg_coherence = sum(record['coherence_score'] for record in self.coherence_history) / total_analyses
        conflict_rate = sum(1 for record in self.coherence_history if record['conflict_count'] > 0) / total_analyses
        
        return {
            'total_analyses': total_analyses,
            'avg_coherence': avg_coherence,
            'conflict_rate': conflict_rate,
            'recent_coherence': self._calculate_recent_coherence()
        }
    
    def _calculate_recent_coherence(self, window: int = 100) -> float:
        """Calculate recent coherence score"""
        recent_analyses = self.coherence_history[-window:]
        if not recent_analyses:
            return 0.0
        
        return sum(record['coherence_score'] for record in recent_analyses) / len(recent_analyses)


def create_meta_coherence_engine() -> MetaCoherenceEngine:
    """Create a new meta-coherence engine"""
    return MetaCoherenceEngine()
