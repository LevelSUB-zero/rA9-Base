"""
Gating Manager - Basal ganglia analogue
Decides what content gets into Working Memory and Global Workspace
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import math

from .schemas import BroadcastItem, AgentOutput, AgentType, NeuromodulatorState, ActiveRepresentation


class GatingPolicy:
    """Base class for gating policies"""
    
    def should_gate(self, item: Any, context: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Determine if an item should be gated through
        
        Args:
            item: Item to evaluate (BroadcastItem, AgentOutput, etc.)
            context: Context including neuromodulator state, resource constraints, etc.
            
        Returns:
            Tuple of (should_gate: bool, confidence: float, reason: str)
        """
        raise NotImplementedError


class DeterministicGatingPolicy(GatingPolicy):
    """Deterministic gating policy based on rules"""
    
    def __init__(self, 
                 min_confidence_threshold: float = 0.3,
                 max_speculative_ratio: float = 0.5,
                 priority_boost_factor: float = 1.2):
        self.min_confidence_threshold = min_confidence_threshold
        self.max_speculative_ratio = max_speculative_ratio
        self.priority_boost_factor = priority_boost_factor
    
    def should_gate(self, item: Any, context: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Apply deterministic gating rules"""
        neuromod_state = context.get('neuromodulator_state', NeuromodulatorState())
        resource_budget = context.get('resource_budget', 1.0)
        current_speculative_ratio = context.get('speculative_ratio', 0.0)
        
        # Extract confidence and other properties
        if isinstance(item, BroadcastItem):
            confidence = item.confidence
            is_speculative = item.speculative
            contributors = item.contributors
        elif isinstance(item, AgentOutput):
            confidence = item.confidence
            is_speculative = False  # Agent outputs are not speculative by default
            contributors = [item.agent]
        else:
            return False, 0.0, "Unknown item type"
        
        # Apply neuromodulator adjustments
        adjusted_confidence = self._apply_neuromodulator_adjustments(
            confidence, neuromod_state, contributors
        )
        
        # Check basic thresholds
        if adjusted_confidence < self.min_confidence_threshold:
            return False, adjusted_confidence, f"Below confidence threshold ({adjusted_confidence:.2f} < {self.min_confidence_threshold})"
        
        # Check speculative ratio limit
        if is_speculative and current_speculative_ratio >= self.max_speculative_ratio:
            return False, adjusted_confidence, f"Speculative ratio limit exceeded ({current_speculative_ratio:.2f} >= {self.max_speculative_ratio})"
        
        # Check resource budget
        if resource_budget < 0.1:  # Low resource budget
            if adjusted_confidence < 0.7:  # Only high-confidence items
                return False, adjusted_confidence, "Low resource budget, only high-confidence items allowed"
        
        # Priority boost for certain agent types
        priority_boost = self._calculate_priority_boost(contributors, context)
        final_confidence = adjusted_confidence * priority_boost
        
        # Final decision
        should_gate = final_confidence >= self.min_confidence_threshold
        
        reason = f"Confidence: {final_confidence:.2f}, Speculative: {is_speculative}, Priority boost: {priority_boost:.2f}"
        
        return should_gate, final_confidence, reason
    
    def _apply_neuromodulator_adjustments(self, confidence: float, 
                                        neuromod_state: NeuromodulatorState,
                                        contributors: List[AgentType]) -> float:
        """Apply neuromodulator-based adjustments to confidence"""
        adjusted_confidence = confidence
        
        # Attention gain (ACh analog) - increases thresholds
        attention_factor = 1.0 + (neuromod_state.attention_gain - 1.0) * 0.3
        adjusted_confidence *= attention_factor
        
        # Exploration noise (NE analog) - affects creative/exploratory agents differently
        if AgentType.CREATIVE in contributors or AgentType.STRATEGIC in contributors:
            explore_factor = 1.0 + neuromod_state.explore_noise * 0.2
            adjusted_confidence *= explore_factor
        
        # Reward signal (DA analog) - boosts recently successful patterns
        if neuromod_state.reward_signal > 0:
            reward_factor = 1.0 + neuromod_state.reward_signal * 0.1
            adjusted_confidence *= reward_factor
        
        return min(adjusted_confidence, 1.0)  # Cap at 1.0
    
    def _calculate_priority_boost(self, contributors: List[AgentType], 
                                context: Dict[str, Any]) -> float:
        """Calculate priority boost based on agent types and context"""
        boost = 1.0
        
        # Context-based boosts
        query_intent = context.get('query_intent', [])
        
        # Boost logical agents for analytical queries
        if 'logical' in query_intent and AgentType.LOGICAL in contributors:
            boost *= self.priority_boost_factor
        
        # Boost creative agents for creative queries
        if 'creative' in query_intent and AgentType.CREATIVE in contributors:
            boost *= self.priority_boost_factor
        
        # Boost verifier agents for factual queries
        if 'factual' in query_intent and AgentType.VERIFIER in contributors:
            boost *= self.priority_boost_factor
        
        # Boost emotional agents for personal queries
        if 'personal' in query_intent and AgentType.EMOTIONAL in contributors:
            boost *= self.priority_boost_factor
        
        return boost


class AdaptiveGatingPolicy(DeterministicGatingPolicy):
    """Adaptive gating policy that learns from feedback"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.learning_rate = 0.01
        self.success_history = []
        self.failure_history = []
        self.adaptive_thresholds = {
            'min_confidence': self.min_confidence_threshold,
            'max_speculative': self.max_speculative_ratio
        }
    
    def should_gate(self, item: Any, context: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Apply adaptive gating with learning"""
        # Get base decision
        should_gate, confidence, reason = super().should_gate(item, context)
        
        # Apply adaptive adjustments
        adaptive_confidence = self._apply_adaptive_adjustments(confidence, context)
        
        # Update thresholds based on history
        self._update_thresholds()
        
        return should_gate, adaptive_confidence, f"{reason} (adaptive: {adaptive_confidence:.2f})"
    
    def _apply_adaptive_adjustments(self, confidence: float, context: Dict[str, Any]) -> float:
        """Apply adaptive adjustments based on learning history"""
        # Simple adaptive adjustment based on recent success/failure
        recent_success_rate = self._calculate_recent_success_rate()
        
        if recent_success_rate > 0.8:  # High success rate
            # Slightly lower threshold to allow more items
            adjustment = 0.95
        elif recent_success_rate < 0.5:  # Low success rate
            # Raise threshold to be more selective
            adjustment = 1.05
        else:
            adjustment = 1.0
        
        return confidence * adjustment
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate recent success rate from history"""
        if not self.success_history and not self.failure_history:
            return 0.5  # Default neutral
        
        recent_success = len([s for s in self.success_history if s > datetime.now().timestamp() - 3600])  # Last hour
        recent_failure = len([f for f in self.failure_history if f > datetime.now().timestamp() - 3600])
        
        total_recent = recent_success + recent_failure
        if total_recent == 0:
            return 0.5
        
        return recent_success / total_recent
    
    def _update_thresholds(self) -> None:
        """Update adaptive thresholds based on performance"""
        success_rate = self._calculate_recent_success_rate()
        
        # Adjust confidence threshold
        if success_rate > 0.8:
            self.adaptive_thresholds['min_confidence'] *= 0.99  # Lower threshold
        elif success_rate < 0.5:
            self.adaptive_thresholds['min_confidence'] *= 1.01  # Raise threshold
        
        # Keep within bounds
        self.adaptive_thresholds['min_confidence'] = max(0.1, min(0.9, self.adaptive_thresholds['min_confidence']))
    
    def record_feedback(self, item_id: str, success: bool, timestamp: float = None) -> None:
        """Record feedback for learning"""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        if success:
            self.success_history.append(timestamp)
        else:
            self.failure_history.append(timestamp)
        
        # Keep only recent history (last 24 hours)
        cutoff = datetime.now().timestamp() - 86400
        self.success_history = [s for s in self.success_history if s > cutoff]
        self.failure_history = [f for f in self.failure_history if f > cutoff]


class GateEngine:
    """
    Main gating engine - coordinates gating decisions
    Analogous to basal ganglia gating in the brain
    """
    
    def __init__(self, policy: Optional[GatingPolicy] = None):
        self.policy = policy or DeterministicGatingPolicy()
        self.gating_history = []
        self.resource_tracker = ResourceTracker()
        # Quarantine holds candidates that fail safety/quality gates (e.g., failed critique/verifier)
        self.quarantine: List[Any] = []
    
    def evaluate_candidates(self, candidates: List[Any], context: Dict[str, Any]) -> List[Any]:
        """
        Evaluate multiple candidates for gating
        
        Args:
            candidates: List of items to evaluate
            context: Context including neuromodulator state, etc.
            
        Returns:
            List of items that passed gating
        """
        gated_items = []
        context = context.copy()
        
        # Update context with current state
        context.update(self._get_current_context())
        
        for candidate in candidates:
            # Safety-first quality gate: require critique pass OR verifier pass
            # Expect metadata on BroadcastItem containing these fields
            quality_allowed = False
            quality_reason = ""
            candidate_metadata = getattr(candidate, 'metadata', {}) or {}
            agent_critique = candidate_metadata.get('agentCritique') or candidate_metadata.get('agent_critique')
            verifier_report = candidate_metadata.get('verifier')
            if isinstance(agent_critique, dict) and agent_critique.get('passed') is True:
                quality_allowed = True
                quality_reason = "agentCritique.pass == True"
            elif isinstance(verifier_report, dict) and verifier_report.get('passed') is True:
                quality_allowed = True
                quality_reason = "verifier.passed == True"

            if not quality_allowed:
                # Quarantine instead of allowing speculative/bad items into workspace
                self.quarantine.append(candidate)
                self._record_gating_decision(
                    candidate,
                    False,
                    0.0,
                    f"Blocked by quality gate: {quality_reason if quality_reason else 'No critic/verifier pass'}"
                )
                continue

            should_gate, confidence, reason = self.policy.should_gate(candidate, context)
            
            # Record gating decision
            self._record_gating_decision(candidate, should_gate, confidence, reason)
            
            if should_gate:
                gated_items.append(candidate)
                
                # Update resource tracking
                self.resource_tracker.consume_resources(candidate)
        
        return gated_items

    def get_quarantine(self) -> List[Any]:
        """Return quarantined items that failed quality gates"""
        return list(self.quarantine)
    
    def evaluate_single(self, item: Any, context: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Evaluate a single item for gating
        
        Args:
            item: Item to evaluate
            context: Context including neuromodulator state, etc.
            
        Returns:
            Tuple of (should_gate: bool, confidence: float, reason: str)
        """
        context = context.copy()
        context.update(self._get_current_context())
        
        should_gate, confidence, reason = self.policy.should_gate(item, context)
        
        # Record gating decision
        self._record_gating_decision(item, should_gate, confidence, reason)
        
        if should_gate:
            self.resource_tracker.consume_resources(item)
        
        return should_gate, confidence, reason
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current context for gating decisions"""
        return {
            'resource_budget': self.resource_tracker.get_remaining_budget(),
            'speculative_ratio': self.resource_tracker.get_speculative_ratio(),
            'gating_history_size': len(self.gating_history),
            'recent_gating_rate': self._calculate_recent_gating_rate()
        }
    
    def _record_gating_decision(self, item: Any, should_gate: bool, 
                              confidence: float, reason: str) -> None:
        """Record a gating decision for analysis"""
        decision = {
            'timestamp': datetime.now(),
            'item_type': type(item).__name__,
            'should_gate': should_gate,
            'confidence': confidence,
            'reason': reason,
            'resource_consumed': self.resource_tracker.estimate_resource_cost(item)
        }
        
        self.gating_history.append(decision)
        
        # Keep only recent history (last 1000 decisions)
        if len(self.gating_history) > 1000:
            self.gating_history = self.gating_history[-1000:]
    
    def _calculate_recent_gating_rate(self) -> float:
        """Calculate recent gating rate (items per minute)"""
        if not self.gating_history:
            return 0.0
        
        now = datetime.now()
        recent_decisions = [d for d in self.gating_history 
                          if (now - d['timestamp']).total_seconds() < 300]  # Last 5 minutes
        
        return len(recent_decisions) / 5.0  # Rate per minute
    
    def get_gating_stats(self) -> Dict[str, Any]:
        """Get gating statistics"""
        if not self.gating_history:
            return {'total_decisions': 0, 'gating_rate': 0.0, 'avg_confidence': 0.0}
        
        total_decisions = len(self.gating_history)
        gated_count = sum(1 for d in self.gating_history if d['should_gate'])
        avg_confidence = sum(d['confidence'] for d in self.gating_history) / total_decisions
        
        return {
            'total_decisions': total_decisions,
            'gating_rate': gated_count / total_decisions,
            'avg_confidence': avg_confidence,
            'recent_gating_rate': self._calculate_recent_gating_rate(),
            'resource_usage': self.resource_tracker.get_usage_stats()
        }


class ResourceTracker:
    """Tracks resource consumption for gating decisions"""
    
    def __init__(self, max_budget: float = 100.0, decay_rate: float = 0.1):
        self.max_budget = max_budget
        self.current_budget = max_budget
        self.decay_rate = decay_rate
        self.last_update = datetime.now()
        self.consumption_history = []
    
    def consume_resources(self, item: Any) -> None:
        """Consume resources for an item"""
        cost = self.estimate_resource_cost(item)
        self.current_budget = max(0, self.current_budget - cost)
        
        self.consumption_history.append({
            'timestamp': datetime.now(),
            'cost': cost,
            'remaining_budget': self.current_budget
        })
        
        # Keep only recent history
        if len(self.consumption_history) > 1000:
            self.consumption_history = self.consumption_history[-1000:]
    
    def estimate_resource_cost(self, item: Any) -> float:
        """Estimate resource cost for an item"""
        if isinstance(item, BroadcastItem):
            # Cost based on confidence and content length
            base_cost = 1.0
            confidence_factor = 1.0 - item.confidence  # Lower confidence = higher cost
            length_factor = len(item.text) / 1000.0  # Longer content = higher cost
            return base_cost + confidence_factor + length_factor
        
        elif isinstance(item, AgentOutput):
            # Cost based on confidence and reasoning trace length
            base_cost = 0.5
            confidence_factor = 1.0 - item.confidence
            trace_factor = len(item.reasoning_trace) / 10.0
            return base_cost + confidence_factor + trace_factor
        
        return 1.0  # Default cost
    
    def get_remaining_budget(self) -> float:
        """Get remaining resource budget"""
        self._apply_decay()
        return self.current_budget
    
    def get_speculative_ratio(self) -> float:
        """Get ratio of speculative items in recent history"""
        if not self.consumption_history:
            return 0.0
        
        recent_items = [h for h in self.consumption_history 
                       if (datetime.now() - h['timestamp']).total_seconds() < 300]
        
        if not recent_items:
            return 0.0
        
        # This is a simplified calculation - in practice, you'd track speculative items separately
        return 0.0  # Placeholder
    
    def _apply_decay(self) -> None:
        """Apply resource budget decay over time"""
        now = datetime.now()
        time_since_update = (now - self.last_update).total_seconds() / 60.0  # minutes
        
        if time_since_update > 0:
            # Restore budget over time
            restoration = self.decay_rate * time_since_update * self.max_budget
            self.current_budget = min(self.max_budget, self.current_budget + restoration)
            self.last_update = now
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get resource usage statistics"""
        self._apply_decay()
        return {
            'current_budget': self.current_budget,
            'max_budget': self.max_budget,
            'usage_percentage': (self.max_budget - self.current_budget) / self.max_budget,
            'recent_consumption': len([h for h in self.consumption_history 
                                    if (datetime.now() - h['timestamp']).total_seconds() < 300])
        }
