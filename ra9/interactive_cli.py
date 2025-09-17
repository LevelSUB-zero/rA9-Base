#!/usr/bin/env python3
"""
Interactive CLI for RA9 Enhanced Workflow
Simple interface to test the new workflow features
"""

import json
import sys
import os
from typing import Dict, Any

# Add the ra9 directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with absolute paths to avoid relative import issues
from core.executor import execute_ra9_multi_agent
from core.engine import load_persona
from core.enhanced_cli_ui import get_cli

def show_help():
    """Show help information"""
    print("""
🧠 RA9 Interactive CLI - Enhanced Workflow Tester

Commands:
  help, h     - Show this help
  quit, q     - Exit the CLI
  clear, c    - Clear screen
  test        - Run a test query
  custom      - Enter custom query with options

Examples:
  test                    - Run a simple test
  custom                  - Enter your own query
  help                    - Show this help
""")

def run_test_query():
    """Run a predefined test query"""
    test_payload = {
        "jobId": "test-001",
        "userId": "demo_user",
        "text": "Plan a 3-step launch strategy for a new AI product and reflect on potential risks.",
        "mode": "deep",
        "loopDepth": 2,
        "allowMemoryWrite": True
    }
    
    print("🚀 Running test query...")
    print(f"Query: {test_payload['text']}")
    print("=" * 80)
    
    try:
        # Run the workflow directly
        cli = get_cli()
        cli.start_session()
        
        persona = load_persona()
        result = execute_ra9_multi_agent(
            test_payload['text'], 
            persona, 
            user_id=test_payload['userId'], 
            allow_memory_write=test_payload['allowMemoryWrite']
        )
        
        cli.end_session()
        print("\n" + "=" * 80)
        print("✅ Test completed successfully!")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Error running test: {e}")

def run_custom_query():
    """Run a custom query with user input"""
    print("\n📝 Custom Query Setup")
    print("-" * 40)
    
    # Get query text
    text = input("Enter your query: ").strip()
    if not text:
        print("❌ No query provided")
        return
    
    # Get mode
    print("\nModes: concise, deep, debate, planner")
    mode = input("Mode (default: deep): ").strip() or "deep"
    
    # Get loop depth
    try:
        loop_depth = int(input("Loop depth (1-6, default: 2): ").strip() or "2")
        loop_depth = max(1, min(6, loop_depth))
    except ValueError:
        loop_depth = 2
    
    # Get memory write preference
    memory_input = input("Allow memory write? (y/n, default: y): ").strip().lower()
    allow_memory = memory_input in ['', 'y', 'yes', 'true']
    
    # Get user ID
    user_id = input("User ID (default: interactive_user): ").strip() or "interactive_user"
    
    # Create payload
    payload = {
        "jobId": f"interactive-{int(time.time())}",
        "userId": user_id,
        "text": text,
        "mode": mode,
        "loopDepth": loop_depth,
        "allowMemoryWrite": allow_memory
    }
    
    print(f"\n🚀 Running custom query...")
    print(f"Query: {text}")
    print(f"Mode: {mode}, Depth: {loop_depth}, Memory: {allow_memory}")
    print("=" * 80)
    
    try:
        # Run the workflow directly
        cli = get_cli()
        cli.start_session()
        
        persona = load_persona()
        result = execute_ra9_multi_agent(
            payload['text'], 
            persona, 
            user_id=payload['userId'], 
            allow_memory_write=payload['allowMemoryWrite']
        )
        
        cli.end_session()
        print("\n" + "=" * 80)
        print("✅ Query completed successfully!")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Error running query: {e}")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main interactive loop"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🧠 RA9 Interactive CLI - Enhanced Workflow Tester                          ║
║  Test the new multi-agent reasoning workflow with real-time visualization   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    print("Welcome to RA9 Interactive CLI!")
    print("Type 'help' for commands or 'test' to run a sample query.")
    print()
    
    while True:
        try:
            command = input("RA9> ").strip().lower()
            
            if command in ['quit', 'q', 'exit']:
                print("👋 Goodbye!")
                break
            elif command in ['help', 'h']:
                show_help()
            elif command in ['clear', 'c']:
                clear_screen()
            elif command == 'test':
                run_test_query()
            elif command == 'custom':
                run_custom_query()
            elif command == '':
                continue
            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")
            
            print()  # Add spacing between commands
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import time
    main()
