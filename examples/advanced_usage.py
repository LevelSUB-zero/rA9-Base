#!/usr/bin/env python3
"""
Advanced usage example for RA9.

This example demonstrates advanced features like memory, multiple iterations,
and custom configuration.
"""

import os
import sys
import json
from pathlib import Path

# Add the package root to the path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from ra9 import run_ra9_cognitive_engine, get_config, get_logger
from ra9.core.config import Config


def demonstrate_memory_system():
    """Demonstrate memory system usage."""
    print("🧠 Memory System Demo")
    print("=" * 50)
    
    # First query - will be stored in memory
    print("📝 First query (will be stored in memory):")
    result1 = run_ra9_cognitive_engine(
        job_id="memory_demo_1",
        job_payload={
            "text": "My name is Alice and I love astronomy",
            "mode": "concise",
            "loopDepth": 1,
            "allowMemoryWrite": True,
            "userId": "alice"
        }
    )
    print(f"Response: {result1.get('final_answer', 'No response')}")
    print()
    
    # Second query - should reference previous memory
    print("📝 Second query (should reference previous memory):")
    result2 = run_ra9_cognitive_engine(
        job_id="memory_demo_2", 
        job_payload={
            "text": "What do you know about me?",
            "mode": "concise",
            "loopDepth": 1,
            "allowMemoryWrite": True,
            "userId": "alice"
        }
    )
    print(f"Response: {result2.get('final_answer', 'No response')}")
    print()


def demonstrate_multiple_iterations():
    """Demonstrate multiple iteration processing."""
    print("🔄 Multiple Iterations Demo")
    print("=" * 50)
    
    result = run_ra9_cognitive_engine(
        job_id="iterations_demo",
        job_payload={
            "text": "Design a sustainable city for 1 million people",
            "mode": "detailed",
            "loopDepth": 3,  # Multiple iterations
            "allowMemoryWrite": False,
            "userId": "planner"
        }
    )
    
    print(f"Final Response: {result.get('final_answer', 'No response')}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Quality Score: {result.get('quality_score', 0)}")
    print()


def demonstrate_different_modes():
    """Demonstrate different processing modes."""
    print("🎭 Different Modes Demo")
    print("=" * 50)
    
    query = "What is the future of artificial intelligence?"
    modes = ["concise", "detailed", "creative", "analytical"]
    
    for mode in modes:
        print(f"📝 Mode: {mode}")
        result = run_ra9_cognitive_engine(
            job_id=f"mode_demo_{mode}",
            job_payload={
                "text": query,
                "mode": mode,
                "loopDepth": 1,
                "allowMemoryWrite": False,
                "userId": "mode_tester"
            }
        )
        
        response = result.get('final_answer', 'No response')
        print(f"Response: {response[:100]}...")
        print()


def demonstrate_custom_configuration():
    """Demonstrate custom configuration."""
    print("⚙️ Custom Configuration Demo")
    print("=" * 50)
    
    # Create custom configuration
    custom_config = Config(
        max_iterations=2,
        default_mode="creative",
        memory_enabled=True,
        enable_reflection=True,
        log_level="DEBUG"
    )
    
    print(f"Custom config: {custom_config.get_agent_config()}")
    
    # Use custom configuration (would need to be set globally)
    # For this example, we'll just show the configuration
    print("Custom configuration created successfully!")
    print()


def demonstrate_error_handling():
    """Demonstrate error handling."""
    print("🚨 Error Handling Demo")
    print("=" * 50)
    
    # Test with empty query
    print("📝 Testing empty query:")
    result = run_ra9_cognitive_engine(
        job_id="error_demo_1",
        job_payload={
            "text": "",
            "mode": "concise",
            "loopDepth": 1,
            "allowMemoryWrite": False,
            "userId": "error_tester"
        }
    )
    
    if "error" in result:
        print(f"✅ Error caught: {result['error']}")
    else:
        print("❌ Error not caught")
    
    print()


def main():
    """Advanced usage example."""
    
    # Setup logging
    logger = get_logger("ra9.advanced_example")
    
    # Get configuration
    config = get_config()
    
    # Check if API keys are configured
    if not config.is_configured():
        print("❌ No API keys configured!")
        print("Please set GEMINI_API_KEY or OPENAI_API_KEY environment variable.")
        return 1
    
    print("✅ RA9 is configured and ready for advanced examples!")
    print(f"📊 Current configuration: {config.get_agent_config()}")
    print()
    
    try:
        # Run demonstrations
        demonstrate_memory_system()
        demonstrate_multiple_iterations()
        demonstrate_different_modes()
        demonstrate_custom_configuration()
        demonstrate_error_handling()
        
        print("🎉 Advanced examples completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in advanced examples: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())