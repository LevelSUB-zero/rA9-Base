#!/usr/bin/env python3
"""
RA9 - Ultra-Deep Cognitive Engine
Main entry point for the RA9 AI system
"""

import os
import sys
from dotenv import load_dotenv
import uuid
import json

from ra9.core.cli_workflow_engine import run_cli_workflow

def get_api_key(api_name: str, env_var: str) -> str:
    key = os.getenv(env_var)
    if not key:
        print(json.dumps({"kind": "token", "agent": "system", "token": f"It looks like you don't have your {api_name} API key set. Please set it as an environment variable or in a .env file."}), flush=True)
        sys.exit(1)
    return key

def main():
    load_dotenv()

    # Debugging: Print current API key status
    current_gemini_key = os.getenv("GEMINI_API_KEY")

    # Prompt for Google API Key if not set
    gemini_api_key = get_api_key("Google", "GEMINI_API_KEY")
    
    # Crucial: Reload .env after potentially saving a new key to ensure it's picked up
    load_dotenv() 

    os.environ["GEMINI_API_KEY"] = gemini_api_key

    # Read the entire JSON payload from stdin
    try:
        input_payload_str = sys.stdin.readline().strip()
        if not input_payload_str:
            print(json.dumps({"kind": "error", "message": "No input payload received via stdin."}), flush=True)
            sys.exit(1)
        job_payload = json.loads(input_payload_str)
        job_id = job_payload.get("jobId", str(uuid.uuid4())) # Use jobId from payload or generate new
    except json.JSONDecodeError:
        print(json.dumps({"kind": "error", "message": "Invalid JSON payload received via stdin."}), flush=True)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"kind": "error", "message": f"Error reading or parsing stdin: {e}"}), flush=True)
        sys.exit(1)

    try:
        # Run the enhanced CLI workflow
        result = run_cli_workflow(job_payload)
        
        # Emit final result for compatibility
        if "final_answer" in result:
            print(json.dumps({"kind": "token", "agent": "actor", "token": result["final_answer"]}), flush=True)
        else:
            print(json.dumps({"kind": "token", "agent": "actor", "token": "Workflow completed but no final answer generated."}), flush=True)
        print(json.dumps({"kind": "done"}), flush=True)
    except KeyboardInterrupt:
        print(json.dumps({"kind": "token", "agent": "system", "token": "RA9 session terminated by user."}), flush=True)
    except Exception as e:
        print(json.dumps({"kind": "token", "agent": "system", "token": f"An unexpected error occurred: {e}"}), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()