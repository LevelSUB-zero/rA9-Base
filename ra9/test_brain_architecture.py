"""
Test script for the new brain-like RA9 architecture
Demonstrates the core components working together
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ra9.core.schemas import Percept, ModalityType, AgentType, BroadcastItem, NeuromodulatorState
from ra9.core.perception_adapter import PerceptionAdapter
from ra9.core.feature_encoders import FeatureEncoderFactory
from ra9.core.global_workspace import GlobalWorkspaceManager
from ra9.core.gating_manager import GateEngine, DeterministicGatingPolicy
from ra9.core.neuromodulation_controller import NeuromodulationController


def test_perception_adapter():
    """Test the PerceptionAdapter"""
    print("🧠 Testing PerceptionAdapter...")
    
    adapter = PerceptionAdapter()
    
    # Test text input
    text_input = "How can I improve my decision-making skills?"
    percept = adapter.process(text_input, {'user_id': 'test_user', 'session_id': 'test_session'})
    
    print(f"  ✓ Modality detected: {percept.modality}")
    print(f"  ✓ Tokens extracted: {len(percept.tokens)}")
    print(f"  ✓ Embedding dimension: {len(percept.embedding)}")
    
    # Test code input
    code_input = "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
    code_percept = adapter.process(code_input, {'user_id': 'test_user'})
    
    print(f"  ✓ Code modality detected: {code_percept.modality}")
    
    return percept


def test_feature_encoders():
    """Test the Feature Encoders"""
    print("\n🔍 Testing Feature Encoders...")
    
    # Test text encoder
    text_input = "What is the meaning of life? This is a deep philosophical question."
    percept = Percept(
        modality=ModalityType.TEXT,
        embedding=[0.1] * 768,
        tokens=text_input.split(),
        raw_text=text_input
    )
    
    features = FeatureEncoderFactory.encode_percept(percept)
    print(f"  ✓ Text features extracted: {len(features)} categories")
    print(f"  ✓ Semantic features: {list(features.get('semantic_features', {}).keys())}")
    print(f"  ✓ Syntactic features: {list(features.get('syntactic_features', {}).keys())}")
    
    # Test code encoder
    code_input = "def calculate_sum(a, b):\n    return a + b"
    code_percept = Percept(
        modality=ModalityType.CODE,
        embedding=[0.2] * 768,
        tokens=code_input.split(),
        raw_text=code_input
    )
    
    code_features = FeatureEncoderFactory.encode_percept(code_percept)
    print(f"  ✓ Code features extracted: {len(code_features)} categories")
    print(f"  ✓ Language detected: {code_features.get('language_features', {}).get('detected_language', 'unknown')}")


def test_global_workspace():
    """Test the Global Workspace and Working Memory"""
    print("\n🌐 Testing Global Workspace...")
    
    gwm = GlobalWorkspaceManager()
    
    # Create some broadcast items
    item1 = BroadcastItem(
        id="item_1",
        text="Logical analysis suggests focusing on data-driven decisions",
        contributors=[AgentType.LOGICAL],
        confidence=0.8
    )
    
    item2 = BroadcastItem(
        id="item_2", 
        text="Creative thinking might reveal innovative approaches",
        contributors=[AgentType.CREATIVE],
        confidence=0.6
    )
    
    # Broadcast items
    gwm.broadcast_and_store(item1)
    gwm.broadcast_and_store(item2)
    
    print(f"  ✓ Items broadcast: 2")
    
    # Test search
    search_results = gwm.global_workspace.search_items("creative", max_results=5)
    print(f"  ✓ Search results: {len(search_results)} items found")
    
    # Test working memory
    wm_stats = gwm.working_memory.get_stats()
    print(f"  ✓ Working memory slots: {wm_stats['active_slots']}/{wm_stats['max_slots']}")
    
    return gwm


def test_gating_manager():
    """Test the Gating Manager"""
    print("\n🚪 Testing Gating Manager...")
    
    policy = DeterministicGatingPolicy(min_confidence_threshold=0.5)
    gate_engine = GateEngine(policy)
    
    # Create test items
    high_confidence_item = BroadcastItem(
        id="high_conf",
        text="High confidence analysis",
        contributors=[AgentType.LOGICAL],
        confidence=0.9
    )
    
    low_confidence_item = BroadcastItem(
        id="low_conf",
        text="Low confidence speculation", 
        contributors=[AgentType.CREATIVE],
        confidence=0.3
    )
    
    # Test gating decisions
    context = {'resource_budget': 1.0, 'speculative_ratio': 0.0}
    
    should_gate_high, conf_high, reason_high = gate_engine.evaluate_single(high_confidence_item, context)
    should_gate_low, conf_low, reason_low = gate_engine.evaluate_single(low_confidence_item, context)
    
    print(f"  ✓ High confidence item gated: {should_gate_high} (confidence: {conf_high:.2f})")
    print(f"  ✓ Low confidence item gated: {should_gate_low} (confidence: {conf_low:.2f})")
    
    # Test batch evaluation
    candidates = [high_confidence_item, low_confidence_item]
    gated_items = gate_engine.evaluate_candidates(candidates, context)
    print(f"  ✓ Batch evaluation: {len(gated_items)}/{len(candidates)} items gated")
    
    return gate_engine


def test_neuromodulation_controller():
    """Test the Neuromodulation Controller"""
    print("\n⚡ Testing Neuromodulation Controller...")
    
    nm_controller = NeuromodulationController()
    
    # Test initial state
    initial_state = nm_controller.get_state()
    print(f"  ✓ Initial attention gain: {initial_state.attention_gain:.2f}")
    print(f"  ✓ Initial explore noise: {initial_state.explore_noise:.2f}")
    print(f"  ✓ Initial reward signal: {initial_state.reward_signal:.2f}")
    
    # Test feedback processing
    nm_controller.process_feedback('success', 0.8, {'context': 'test'})
    nm_controller.process_feedback('novelty', 0.6, {'context': 'test'})
    
    updated_state = nm_controller.get_state()
    print(f"  ✓ Updated attention gain: {updated_state.attention_gain:.2f}")
    print(f"  ✓ Updated explore noise: {updated_state.explore_noise:.2f}")
    print(f"  ✓ Updated reward signal: {updated_state.reward_signal:.2f}")
    
    # Test agent behavior modulation
    modulations = nm_controller.modulate_agent_behavior(
        AgentType.CREATIVE, 
        base_confidence=0.7, 
        base_temperature=0.8
    )
    print(f"  ✓ Creative agent modulations: {list(modulations.keys())}")
    print(f"  ✓ Modulated confidence: {modulations['confidence']:.2f}")
    print(f"  ✓ Modulated temperature: {modulations['temperature']:.2f}")
    
    return nm_controller


def test_integrated_workflow():
    """Test the integrated workflow"""
    print("\n🔄 Testing Integrated Workflow...")
    
    # Initialize all components
    adapter = PerceptionAdapter()
    gwm = GlobalWorkspaceManager()
    gate_engine = GateEngine()
    nm_controller = NeuromodulationController()
    
    # Process input
    query = "How can I be more creative in my work?"
    percept = adapter.process(query, {'user_id': 'test_user'})
    features = FeatureEncoderFactory.encode_percept(percept)
    
    print(f"  ✓ Query processed: '{query}'")
    print(f"  ✓ Modality: {percept.modality}")
    print(f"  ✓ Features extracted: {len(features)} categories")
    
    # Simulate agent outputs
    creative_output = BroadcastItem(
        id="creative_1",
        text="Try brainstorming sessions, mind mapping, and exploring new perspectives",
        contributors=[AgentType.CREATIVE],
        confidence=0.8
    )
    
    logical_output = BroadcastItem(
        id="logical_1", 
        text="Systematic approaches include structured creativity techniques and regular practice",
        contributors=[AgentType.LOGICAL],
        confidence=0.7
    )
    
    # Get neuromodulator state for gating
    nm_state = nm_controller.get_state()
    context = {
        'neuromodulator_state': nm_state,
        'resource_budget': 1.0,
        'speculative_ratio': 0.0,
        'query_intent': ['creative', 'strategic']
    }
    
    # Gate the outputs
    gated_items = gate_engine.evaluate_candidates([creative_output, logical_output], context)
    print(f"  ✓ Agent outputs gated: {len(gated_items)}/{2}")
    
    # Broadcast gated items
    for item in gated_items:
        gwm.broadcast_and_store(item)
    
    # Process feedback
    nm_controller.process_feedback('success', 0.9, {'context': 'creative_query'})
    
    print(f"  ✓ Workflow completed successfully!")
    
    return {
        'percept': percept,
        'features': features,
        'gated_items': gated_items,
        'nm_state': nm_controller.get_state()
    }


def main():
    """Run all tests"""
    print("🧠 RA9 Brain-Like Architecture Test Suite")
    print("=" * 50)
    
    try:
        # Test individual components
        percept = test_perception_adapter()
        test_feature_encoders()
        gwm = test_global_workspace()
        gate_engine = test_gating_manager()
        nm_controller = test_neuromodulation_controller()
        
        # Test integrated workflow
        workflow_result = test_integrated_workflow()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\n🎯 Key Achievements:")
        print("  • Multimodal perception and feature extraction")
        print("  • Global workspace with pub/sub broadcasting")
        print("  • Intelligent gating with resource management")
        print("  • Neuromodulation-based behavior adaptation")
        print("  • Integrated workflow simulation")
        
        print(f"\n📊 Final Stats:")
        print(f"  • Working Memory: {gwm.working_memory.get_stats()['active_slots']} active slots")
        print(f"  • Gating Rate: {gate_engine.get_gating_stats()['gating_rate']:.2%}")
        print(f"  • Attention Gain: {nm_controller.get_state().attention_gain:.2f}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
