#!/usr/bin/env python3
"""
Basic usage example for RA9.

This example demonstrates how to use RA9 programmatically.
"""

import os
import sys
from pathlib import Path

# Add the package root to the path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from ra9 import run_ra9_cognitive_engine, get_config, get_logger
from ra9.core.config import Config


def main():
    """Basic usage example."""
    
    # Setup logging
    logger = get_logger("ra9.example")
    
    # Get configuration
    config = get_config()
    
    # Check if API keys are configured
    if not config.is_configured():
        print("❌ No API keys configured!")
        print("Please set GEMINI_API_KEY or OPENAI_API_KEY environment variable.")
        print("You can also create a .env file with your API keys.")
        return 1
    
    print("✅ RA9 is configured and ready!")
    print(f"📊 Configuration: {config.get_agent_config()}")
    
    # Example queries
    queries = [
        {
            "text": "What is artificial intelligence?",
            "mode": "concise",
            "description": "Basic AI question"
        },
        {
            "text": "Explain quantum computing in simple terms",
            "mode": "detailed", 
            "description": "Complex technical topic"
        },
        {
            "text": "Write a creative story about a robot learning to paint",
            "mode": "creative",
            "description": "Creative writing task"
        },
        {
            "text": "Analyze the pros and cons of renewable energy",
            "mode": "analytical",
            "description": "Analytical reasoning task"
        }
    ]
    
    print("\n🚀 Running example queries...\n")
    
    for i, query_data in enumerate(queries, 1):
        print(f"📝 Query {i}: {query_data['description']}")
        print(f"   Mode: {query_data['mode']}")
        print(f"   Text: {query_data['text'][:50]}...")
        
        try:
            # Process the query
            result = run_ra9_cognitive_engine(
                job_id=f"example_{i}",
                job_payload={
                    "text": query_data["text"],
                    "mode": query_data["mode"],
                    "loopDepth": 1,
                    "allowMemoryWrite": False,  # Don't store in memory for examples
                    "userId": "example_user"
                }
            )
            
            # Display result
            if "final_answer" in result:
                print(f"✅ Response: {result['final_answer'][:100]}...")
            else:
                print("❌ No response generated")
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            
            print()
            
        except Exception as e:
            logger.error(f"Error processing query {i}: {e}")
            print(f"❌ Error: {e}")
            print()
    
    print("🎉 Example completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
