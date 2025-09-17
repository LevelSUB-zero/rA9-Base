"""
Neuromodulation Controller - Global scalar modulators analogue
Manages attention, exploration, and reward signals that modulate system behavior
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import json
import math

from .schemas import NeuromodulatorState, AgentType, BroadcastItem, AgentOutput


class NeuromodulationController:
    """
    Neuromodulation Controller - manages global scalar modulators
    Analogous to neuromodulators (ACh, NE, DA) in the brain
    """
    
    def __init__(self):
        self.state = NeuromodulatorState()
        self.lock = threading.RLock()
        self.update_callbacks: List[Callable[[NeuromodulatorState], None]] = []
        
        # Learning parameters
        self.learning_rate = 0.01
        self.decay_rate = 0.001  # Natural decay over time
        self.reward_history = []
        self.attention_history = []
        self.exploration_history = []
        
        # Adaptive thresholds
        self.adaptive_thresholds = {
            'attention_gain': {'min': 0.1, 'max': 2.0, 'target': 1.0},
            'explore_noise': {'min': 0.0, 'max': 1.0, 'target': 0.2},
            'reward_signal': {'min': -1.0, 'max': 1.0, 'target': 0.0}
        }
    
    def get_state(self) -> NeuromodulatorState:
        """Get current neuromodulator state"""
        with self.lock:
            self._apply_decay()
            return NeuromodulatorState(
                attention_gain=self.state.attention_gain,
                explore_noise=self.state.explore_noise,
                reward_signal=self.state.reward_signal,
                timestamp=datetime.now()
            )
    
    def update_attention_gain(self, delta: float, reason: str = "") -> None:
        """
        Update attention gain (ACh analog)
        
        Args:
            delta: Change in attention gain (-1.0 to 1.0)
            reason: Reason for the update
        """
        with self.lock:
            old_value = self.state.attention_gain
            self.state.attention_gain = self._clamp_value(
                self.state.attention_gain + delta,
                self.adaptive_thresholds['attention_gain']
            )
            
            self._record_update('attention_gain', old_value, self.state.attention_gain, reason)
            self._notify_callbacks()
    
    def update_explore_noise(self, delta: float, reason: str = "") -> None:
        """
        Update exploration noise (NE analog)
        
        Args:
            delta: Change in exploration noise (-1.0 to 1.0)
            reason: Reason for the update
        """
        with self.lock:
            old_value = self.state.explore_noise
            self.state.explore_noise = self._clamp_value(
                self.state.explore_noise + delta,
                self.adaptive_thresholds['explore_noise']
            )
            
            self._record_update('explore_noise', old_value, self.state.explore_noise, reason)
            self._notify_callbacks()
    
    def update_reward_signal(self, delta: float, reason: str = "") -> None:
        """
        Update reward signal (DA analog)
        
        Args:
            delta: Change in reward signal (-1.0 to 1.0)
            reason: Reason for the update
        """
        with self.lock:
            old_value = self.state.reward_signal
            self.state.reward_signal = self._clamp_value(
                self.state.reward_signal + delta,
                self.adaptive_thresholds['reward_signal']
            )
            
            self._record_update('reward_signal', old_value, self.state.reward_signal, reason)
            self._notify_callbacks()
    
    def process_feedback(self, feedback_type: str, value: float, context: Dict[str, Any] = None) -> None:
        """
        Process feedback and update neuromodulators accordingly
        
        Args:
            feedback_type: Type of feedback ('success', 'failure', 'uncertainty', 'novelty')
            value: Feedback value (0.0 to 1.0)
            context: Additional context
        """
        if context is None:
            context = {}
        
        with self.lock:
            if feedback_type == 'success':
                self._handle_success_feedback(value, context)
            elif feedback_type == 'failure':
                self._handle_failure_feedback(value, context)
            elif feedback_type == 'uncertainty':
                self._handle_uncertainty_feedback(value, context)
            elif feedback_type == 'novelty':
                self._handle_novelty_feedback(value, context)
            elif feedback_type == 'user_engagement':
                self._handle_engagement_feedback(value, context)
            else:
                print(f"Unknown feedback type: {feedback_type}")
    
    def modulate_agent_behavior(self, agent_type: AgentType, base_confidence: float, 
                              base_temperature: float = 0.7) -> Dict[str, float]:
        """
        Modulate agent behavior based on current neuromodulator state
        
        Args:
            agent_type: Type of agent
            base_confidence: Base confidence level
            base_temperature: Base temperature for sampling
            
        Returns:
            Dict with modulated parameters
        """
        with self.lock:
            self._apply_decay()
            
            # Attention gain affects confidence thresholds
            attention_factor = self.state.attention_gain
            modulated_confidence = base_confidence * attention_factor
            
            # Exploration noise and attention affect temperature and creativity
            explore_factor = 1.0 + self.state.explore_noise
            # Higher attention reduces temperature (more deterministic)
            modulated_temperature = base_temperature / max(self.state.attention_gain, 0.1)
            
            # Reward signal affects learning rate and persistence
            reward_factor = 1.0 + (self.state.reward_signal * 0.5)
            modulated_learning_rate = self.learning_rate * reward_factor
            
            # Agent-specific modulations
            agent_modulations = self._get_agent_specific_modulations(agent_type)
            
            return {
                'confidence': min(modulated_confidence, 1.0),
                'temperature': min(modulated_temperature, 2.0),
                'learning_rate': modulated_learning_rate,
                'attention_factor': attention_factor,
                'explore_factor': explore_factor,
                'reward_factor': reward_factor,
                **agent_modulations
            }
    
    def modulate_gating_thresholds(self, base_threshold: float) -> float:
        """
        Modulate gating thresholds based on neuromodulator state
        
        Args:
            base_threshold: Base gating threshold
            
        Returns:
            Modulated threshold
        """
        with self.lock:
            # Higher attention gain = higher thresholds (more selective)
            attention_factor = 1.0 + (self.state.attention_gain - 1.0) * 0.3
            
            # Higher reward signal = lower thresholds (more permissive)
            reward_factor = 1.0 - (self.state.reward_signal * 0.2)
            
            modulated_threshold = base_threshold * attention_factor * reward_factor
            
            return max(0.1, min(0.9, modulated_threshold))
    
    def add_update_callback(self, callback: Callable[[NeuromodulatorState], None]) -> None:
        """Add callback for neuromodulator state updates"""
        with self.lock:
            self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[NeuromodulatorState], None]) -> None:
        """Remove update callback"""
        with self.lock:
            if callback in self.update_callbacks:
                self.update_callbacks.remove(callback)
    
    def _apply_decay(self) -> None:
        """Apply natural decay to neuromodulator values"""
        now = datetime.now()
        time_since_update = (now - self.state.timestamp).total_seconds() / 3600.0  # hours
        
        if time_since_update > 0:
            # Decay towards target values
            self.state.attention_gain = self._decay_towards_target(
                self.state.attention_gain, 
                self.adaptive_thresholds['attention_gain']['target'],
                time_since_update
            )
            
            self.state.explore_noise = self._decay_towards_target(
                self.state.explore_noise,
                self.adaptive_thresholds['explore_noise']['target'],
                time_since_update
            )
            
            self.state.reward_signal = self._decay_towards_target(
                self.state.reward_signal,
                self.adaptive_thresholds['reward_signal']['target'],
                time_since_update
            )
            
            self.state.timestamp = now
    
    def _decay_towards_target(self, current: float, target: float, time_delta: float) -> float:
        """Decay current value towards target over time"""
        decay_amount = self.decay_rate * time_delta
        if current > target:
            return max(target, current - decay_amount)
        else:
            return min(target, current + decay_amount)
    
    def _clamp_value(self, value: float, thresholds: Dict[str, float]) -> float:
        """Clamp value within thresholds"""
        return max(thresholds['min'], min(thresholds['max'], value))
    
    def _record_update(self, modulator: str, old_value: float, new_value: float, reason: str) -> None:
        """Record neuromodulator update for analysis"""
        update_record = {
            'timestamp': datetime.now(),
            'modulator': modulator,
            'old_value': old_value,
            'new_value': new_value,
            'delta': new_value - old_value,
            'reason': reason
        }
        
        if modulator == 'attention_gain':
            self.attention_history.append(update_record)
        elif modulator == 'explore_noise':
            self.exploration_history.append(update_record)
        elif modulator == 'reward_signal':
            self.reward_history.append(update_record)
        
        # Keep only recent history (last 1000 updates)
        for history in [self.attention_history, self.exploration_history, self.reward_history]:
            if len(history) > 1000:
                history[:] = history[-1000:]
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of state changes"""
        for callback in self.update_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                print(f"Error in neuromodulator callback: {e}")
    
    def _handle_success_feedback(self, value: float, context: Dict[str, Any]) -> None:
        """Handle success feedback"""
        # Success increases reward signal and attention gain
        reward_delta = value * 0.1
        attention_delta = value * 0.05
        
        self.update_reward_signal(reward_delta, f"Success feedback: {value}")
        self.update_attention_gain(attention_delta, f"Success feedback: {value}")
    
    def _handle_failure_feedback(self, value: float, context: Dict[str, Any]) -> None:
        """Handle failure feedback"""
        # Failure decreases reward signal and increases exploration
        reward_delta = -value * 0.1
        explore_delta = value * 0.1
        
        self.update_reward_signal(reward_delta, f"Failure feedback: {value}")
        self.update_explore_noise(explore_delta, f"Failure feedback: {value}")
    
    def _handle_uncertainty_feedback(self, value: float, context: Dict[str, Any]) -> None:
        """Handle uncertainty feedback"""
        # Uncertainty increases exploration and attention
        explore_delta = value * 0.15
        attention_delta = value * 0.1
        
        self.update_explore_noise(explore_delta, f"Uncertainty feedback: {value}")
        self.update_attention_gain(attention_delta, f"Uncertainty feedback: {value}")
    
    def _handle_novelty_feedback(self, value: float, context: Dict[str, Any]) -> None:
        """Handle novelty feedback"""
        # Novelty increases exploration and reward
        explore_delta = value * 0.2
        reward_delta = value * 0.05
        
        self.update_explore_noise(explore_delta, f"Novelty feedback: {value}")
        self.update_reward_signal(reward_delta, f"Novelty feedback: {value}")
    
    def _handle_engagement_feedback(self, value: float, context: Dict[str, Any]) -> None:
        """Handle user engagement feedback"""
        # High engagement increases reward and attention
        reward_delta = value * 0.08
        attention_delta = value * 0.06
        
        self.update_reward_signal(reward_delta, f"Engagement feedback: {value}")
        self.update_attention_gain(attention_delta, f"Engagement feedback: {value}")
    
    def _get_agent_specific_modulations(self, agent_type: AgentType) -> Dict[str, float]:
        """Get agent-specific modulation parameters"""
        modulations = {}
        
        if agent_type == AgentType.CREATIVE:
            # Creative agents benefit from higher exploration
            modulations['creativity_boost'] = 1.0 + self.state.explore_noise * 0.5
            modulations['novelty_threshold'] = 0.5 - (self.state.explore_noise * 0.3)
        
        elif agent_type == AgentType.LOGICAL:
            # Logical agents benefit from higher attention
            modulations['precision_boost'] = 1.0 + (self.state.attention_gain - 1.0) * 0.3
            modulations['confidence_threshold'] = 0.7 + (self.state.attention_gain - 1.0) * 0.2
        
        elif agent_type == AgentType.EMOTIONAL:
            # Emotional agents are sensitive to reward signals
            modulations['empathy_boost'] = 1.0 + self.state.reward_signal * 0.4
            modulations['sensitivity'] = 0.5 + self.state.reward_signal * 0.3
        
        elif agent_type == AgentType.STRATEGIC:
            # Strategic agents balance exploration and attention
            modulations['planning_horizon'] = 1.0 + self.state.explore_noise * 0.3
            modulations['risk_tolerance'] = 0.5 + self.state.reward_signal * 0.2
        
        elif agent_type == AgentType.VERIFIER:
            # Verifier agents benefit from high attention
            modulations['verification_strictness'] = 1.0 + (self.state.attention_gain - 1.0) * 0.4
            modulations['evidence_threshold'] = 0.8 + (self.state.attention_gain - 1.0) * 0.1
        
        return modulations
    
    def get_adaptive_thresholds(self) -> Dict[str, Any]:
        """Get current adaptive thresholds"""
        with self.lock:
            return {
                'attention_gain': {
                    'current': self.state.attention_gain,
                    'target': self.adaptive_thresholds['attention_gain']['target'],
                    'range': (self.adaptive_thresholds['attention_gain']['min'], 
                             self.adaptive_thresholds['attention_gain']['max'])
                },
                'explore_noise': {
                    'current': self.state.explore_noise,
                    'target': self.adaptive_thresholds['explore_noise']['target'],
                    'range': (self.adaptive_thresholds['explore_noise']['min'], 
                             self.adaptive_thresholds['explore_noise']['max'])
                },
                'reward_signal': {
                    'current': self.state.reward_signal,
                    'target': self.adaptive_thresholds['reward_signal']['target'],
                    'range': (self.adaptive_thresholds['reward_signal']['min'], 
                             self.adaptive_thresholds['reward_signal']['max'])
                }
            }
    
    def get_history_stats(self) -> Dict[str, Any]:
        """Get statistics from neuromodulator history"""
        with self.lock:
            return {
                'attention_updates': len(self.attention_history),
                'exploration_updates': len(self.exploration_history),
                'reward_updates': len(self.reward_history),
                'recent_attention_trend': self._calculate_trend(self.attention_history),
                'recent_exploration_trend': self._calculate_trend(self.exploration_history),
                'recent_reward_trend': self._calculate_trend(self.reward_history)
            }
    
    def _calculate_trend(self, history: List[Dict[str, Any]], window: int = 10) -> float:
        """Calculate trend in recent updates"""
        if len(history) < 2:
            return 0.0
        
        recent_updates = history[-window:]
        if len(recent_updates) < 2:
            return 0.0
        
        # Calculate average delta
        avg_delta = sum(update['delta'] for update in recent_updates) / len(recent_updates)
        return avg_delta
