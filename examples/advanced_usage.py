#!/usr/bin/env python3
"""
RA9 Advanced Usage Examples
Demonstrates various features and capabilities of the RA9 Cognitive Engine
"""

import json
import time
from typing import Dict, Any
from ra9.core.cli_workflow_engine import run_cli_workflow
from ra9.core.cli_quality_summary import run_quality_summary
from ra9.test_complete_brain_architecture import test_complete_brain_workflow

def example_basic_query():
    """Basic query processing example"""
    print("🤖 Example 1: Basic Query Processing")
    print("=" * 50)
    
    query = {
        "jobId": "basic-1",
        "text": "What are the key principles of sustainable development?",
        "mode": "deep",
        "loopDepth": 2,
        "allowMemoryWrite": False
    }
    
    print(f"Query: {query['text']}")
    print("Processing...")
    
    result = run_cli_workflow(query)
    
    if "final_answer" in result:
        print(f"\n📝 Response: {result['final_answer']}")
    else:
        print("\n⚠️  No response generated")
    
    return result

def example_complex_analysis():
    """Complex multi-step analysis example"""
    print("\n🧠 Example 2: Complex Multi-Agent Analysis")
    print("=" * 50)
    
    query = {
        "jobId": "complex-1",
        "text": "Analyze the potential impact of quantum computing on cybersecurity, considering both opportunities and threats. Provide a strategic roadmap for organizations.",
        "mode": "hybrid",
        "loopDepth": 3,
        "allowMemoryWrite": True
    }
    
    print(f"Query: {query['text']}")
    print("Processing with multiple agents...")
    
    result = run_cli_workflow(query)
    
    if "final_answer" in result:
        print(f"\n📝 Comprehensive Analysis: {result['final_answer']}")
    
    # Show processing details
    if "iteration_trace" in result:
        trace = result["iteration_trace"]
        print(f"\n📊 Processing Details:")
        print(f"  - Iterations: {len(trace)}")
        for i, iteration in enumerate(trace):
            agents = len(iteration.get('agentOutputs', []))
            critiques = len(iteration.get('criticReports', []))
            coherence = iteration.get('coherence', {}).get('coherence_score', 'N/A')
            print(f"  - Iteration {i+1}: {agents} agents, {critiques} critiques, coherence: {coherence}")
    
    return result

def example_quality_monitoring():
    """Quality monitoring and metrics example"""
    print("\n📊 Example 3: Quality Monitoring")
    print("=" * 50)
    
    # Run a test query
    query = {
        "jobId": "quality-test",
        "text": "Explain the concept of artificial general intelligence",
        "mode": "deep",
        "loopDepth": 2,
        "allowMemoryWrite": False
    }
    
    print("Running quality test...")
    result = run_cli_workflow(query)
    
    # Get quality metrics
    print("\n📈 Quality Metrics:")
    try:
        metrics = run_quality_summary()
        print(f"  - Broadcast Count: {metrics.get('broadcast_count', 'N/A')}")
        print(f"  - Quarantine Count: {metrics.get('quarantine_count', 'N/A')}")
        print(f"  - Coherence Score: {metrics.get('coherence', 'N/A')}")
        print(f"  - Critique Pass Rate: {metrics.get('critique_pass_rate', 'N/A')}")
    except Exception as e:
        print(f"  ⚠️  Could not retrieve metrics: {e}")
    
    return result

def example_memory_integration():
    """Memory integration and context example"""
    print("\n🧠 Example 4: Memory Integration")
    print("=" * 50)
    
    # First query - establish context
    query1 = {
        "jobId": "memory-1",
        "text": "I'm working on a machine learning project for image recognition. What are the key considerations?",
        "mode": "deep",
        "loopDepth": 2,
        "allowMemoryWrite": True
    }
    
    print("First query (establishing context):")
    print(f"Query: {query1['text']}")
    result1 = run_cli_workflow(query1)
    
    if "final_answer" in result1:
        print(f"Response: {result1['final_answer'][:200]}...")
    
    # Second query - should use context from first
    query2 = {
        "jobId": "memory-2",
        "text": "What specific algorithms would you recommend for my project?",
        "mode": "deep",
        "loopDepth": 2,
        "allowMemoryWrite": True
    }
    
    print("\nSecond query (using context):")
    print(f"Query: {query2['text']}")
    result2 = run_cli_workflow(query2)
    
    if "final_answer" in result2:
        print(f"Response: {result2['final_answer'][:200]}...")
    
    return result1, result2

def example_error_handling():
    """Error handling and edge cases example"""
    print("\n⚠️  Example 5: Error Handling")
    print("=" * 50)
    
    # Test with invalid input
    try:
        invalid_query = {
            "jobId": "error-test",
            "text": "",  # Empty query
            "mode": "deep",
            "loopDepth": 1,
            "allowMemoryWrite": False
        }
        
        print("Testing empty query...")
        result = run_cli_workflow(invalid_query)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Expected error handled: {e}")
    
    # Test with very complex query
    try:
        complex_query = {
            "jobId": "complex-test",
            "text": "Design a comprehensive framework for ethical AI governance that addresses bias, transparency, accountability, and human rights while considering technical feasibility, economic impact, regulatory compliance, international cooperation, and long-term societal implications. Include specific implementation strategies, risk mitigation approaches, and success metrics.",
            "mode": "hybrid",
            "loopDepth": 4,
            "allowMemoryWrite": True
        }
        
        print("\nTesting very complex query...")
        start_time = time.time()
        result = run_cli_workflow(complex_query)
        end_time = time.time()
        
        print(f"Processing time: {end_time - start_time:.2f} seconds")
        if "final_answer" in result:
            print(f"Response length: {len(result['final_answer'])} characters")
        
    except Exception as e:
        print(f"Complex query error: {e}")

def example_custom_configuration():
    """Custom configuration and tuning example"""
    print("\n⚙️  Example 6: Custom Configuration")
    print("=" * 50)
    
    # This would demonstrate how to modify configuration
    # For now, we'll show the concept
    print("Custom configuration example:")
    print("1. Modify ra9/core/config.py for system-wide settings")
    print("2. Use environment variables for runtime configuration")
    print("3. Adjust agent-specific parameters")
    print("4. Tune quality gates and thresholds")
    
    # Example of accessing current configuration
    try:
        from ra9.core.config import CRITIC_MAX_ALLOWED_ISSUES, COHERENCE_THRESHOLD
        print(f"\nCurrent configuration:")
        print(f"  - Critic Max Issues: {CRITIC_MAX_ALLOWED_ISSUES}")
        print(f"  - Coherence Threshold: {COHERENCE_THRESHOLD}")
    except ImportError:
        print("Configuration module not available")

def run_all_examples():
    """Run all examples in sequence"""
    print("🚀 RA9 Advanced Usage Examples")
    print("=" * 60)
    print("This script demonstrates various RA9 capabilities")
    print("=" * 60)
    
    try:
        # Run examples
        example_basic_query()
        example_complex_analysis()
        example_quality_monitoring()
        example_memory_integration()
        example_error_handling()
        example_custom_configuration()
        
        print("\n✅ All examples completed successfully!")
        print("\nFor more information, see:")
        print("- README.md: Complete setup and usage guide")
        print("- ARCHITECTURE.md: Detailed system architecture")
        print("- tests/: Comprehensive test suites")
        
    except KeyboardInterrupt:
        print("\n\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        print("Check your setup and configuration")

if __name__ == "__main__":
    run_all_examples()
