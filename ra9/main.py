#!/usr/bin/env python3
"""
RA9 - Ultra-Deep Cognitive Engine
Main entry point for the RA9 AI system (legacy compatibility)
"""

import os
import sys
import json
import uuid
from pathlib import Path

# Add the package root to the path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from ra9.core.config import get_config
from ra9.core.logger import setup_logging, get_logger
from ra9.core.cli_workflow_engine import run_cli_workflow


def main():
    """Main entry point for legacy compatibility."""
    
    # Setup basic logging
    setup_logging(log_level="INFO")
    logger = get_logger("ra9.main")
    
    # Load configuration
    config = get_config()
    
    # Check if API keys are configured
    if not config.is_configured():
        print(json.dumps({
            "kind": "error", 
            "message": "No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY environment variable."
        }), flush=True)
        sys.exit(1)

    # Read the entire JSON payload from stdin
    try:
        input_payload_str = sys.stdin.readline().strip()
        if not input_payload_str:
            print(json.dumps({
                "kind": "error", 
                "message": "No input payload received via stdin."
            }), flush=True)
            sys.exit(1)
            
        job_payload = json.loads(input_payload_str)
        job_id = job_payload.get("jobId", str(uuid.uuid4()))
        
        logger.info(f"Processing job {job_id}")
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "kind": "error", 
            "message": f"Invalid JSON payload received via stdin: {e}"
        }), flush=True)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "kind": "error", 
            "message": f"Error reading or parsing stdin: {e}"
        }), flush=True)
        sys.exit(1)

    try:
        # Run the enhanced CLI workflow
        result = run_cli_workflow(job_payload)
        
        # Check if there was an error in the workflow
        if "error" in result:
            print(json.dumps({
                "kind": "error", 
                "message": result["error"]
            }), flush=True)
            sys.exit(1)
        
        # Emit final result for compatibility
        if "final_answer" in result:
            print(json.dumps({
                "kind": "token", 
                "agent": "actor", 
                "token": result["final_answer"]
            }), flush=True)
        else:
            print(json.dumps({
                "kind": "token", 
                "agent": "actor", 
                "token": "Workflow completed but no final answer generated."
            }), flush=True)
            
        print(json.dumps({"kind": "done"}), flush=True)
        
    except KeyboardInterrupt:
        print(json.dumps({
            "kind": "token", 
            "agent": "system", 
            "token": "RA9 session terminated by user."
        }), flush=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(json.dumps({
            "kind": "error", 
            "message": f"An unexpected error occurred: {e}"
        }), flush=True)
        import traceback
        print(json.dumps({
            "kind": "error", 
            "message": f"Traceback: {traceback.format_exc()}"
        }), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()