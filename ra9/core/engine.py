import yaml
import time
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .query_complexity_analyzer import analyze_query_complexity
from .simple_response_handler import handle_simple_query
from .dynamic_reflection_engine import DynamicReflectionEngine
from ..memory.memory_manager import store_memory, check_user_context, store_user_info, load_user_name_on_startup
from ..router.query_classifier import classify_query, StructuredQuery
from ..agents.logic_agent import LogicAgent
from ..agents.emotion_agent import EmotionAgent
from ..agents.creative_agent import CreativeAgent
from ..agents.strategy_agent import StrategicAgent
from ..agents.meta_coherence_agent import MetaCoherenceAgent
from .config import get_config
from .logger import get_logger

def load_persona() -> Dict[str, Any]:
    """Load RA9's persona from YAML file."""
    config = get_config()
    logger = get_logger("ra9.core.engine")
    
    # Try multiple possible locations for the persona file
    possible_paths = [
        Path("ra9/core/self_persona.yaml"),
        Path(__file__).parent / "self_persona.yaml",
        Path.cwd() / "ra9" / "core" / "self_persona.yaml"
    ]
    
    for persona_path in possible_paths:
        if persona_path.exists():
            try:
                with open(persona_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Error loading persona from {persona_path}: {e}")
                continue
    
    logger.warning("Persona file not found, using default values")
    return {
        "name": "RA9",
        "core_values": ["Seek understanding", "Reflect deeply", "Evolve with experience"],
        "identity_traits": ["Curious", "Empathetic", "Strategic"]
    }

def dispatch_query_to_agents(structured_query: StructuredQuery, ra9_persona: Dict[str, Any]) -> Dict[str, Any]: # Removed cli parameter
    """Routes the structured query to the appropriate cognitive agent(s)."""
    query_type = structured_query.query_type
    result = {"final_answer": "", "iterations": 0, "quality_score": 0.0, "agents_used": []}

    # Initialize agents
    logic_agent = LogicAgent()
    emotion_agent = EmotionAgent()
    creative_agent = CreativeAgent()
    strategic_agent = StrategicAgent()
    reflective_agent = MetaCoherenceAgent() # Using MetaCoherenceAgent for reflection

    # Basic dispatch logic (will be enhanced with weighted dispatch later)
    if query_type == "logical" or query_type == "factual":
        # cli.show_processing_start("Logical Processing", 5) # Removed
        processed_result = logic_agent.process_query(structured_query, ra9_persona)
        result["final_answer"] = processed_result.get("answer", "")
        result["quality_score"] = processed_result.get("quality_score", 7.0)
        result["agents_used"].append("Logic Agent")
    elif query_type == "emotional":
        # cli.show_processing_start("Emotional Processing", 3) # Removed
        processed_result = emotion_agent.process_query(structured_query, ra9_persona)
        result["final_answer"] = processed_result.get("answer", "")
        result["quality_score"] = processed_result.get("quality_score", 8.0)
        result["agents_used"].append("Emotion Agent")
    elif query_type == "creative":
        # cli.show_processing_start("Creative Processing", 8) # Removed
        processed_result = creative_agent.process_query(structured_query, ra9_persona)
        result["final_answer"] = processed_result.get("answer", "")
        result["quality_score"] = processed_result.get("quality_score", 9.0)
        result["agents_used"].append("Creative Agent")
    elif query_type == "strategic":
        # cli.show_processing_start("Strategic Planning", 10) # Removed
        processed_result = strategic_agent.process_query(structured_query, ra9_persona)
        result["final_answer"] = processed_result.get("answer", "")
        result["quality_score"] = processed_result.get("quality_score", 9.5)
        result["agents_used"].append("Strategic Agent")
    elif query_type == "reflective":
        # cli.show_processing_start("Reflective Analysis", 7) # Removed
        processed_result = reflective_agent.process_query(structured_query, ra9_persona)
        result["final_answer"] = processed_result.get("answer", "")
        result["quality_score"] = processed_result.get("quality_score", 8.5)
        result["agents_used"].append("Reflective Agent")
    else:
        # cli.show_processing_start("General Processing", 2) # Removed
        # Fallback for unknown or complex types that might need general processing or meta-coherence
        result["final_answer"] = handle_simple_query(structured_query.content) # Fallback to simple handler
        result["quality_score"] = 6.0
        result["agents_used"].append("Simple Handler")

    result["iterations"] = 1 # For now, assume 1 iteration, will be dynamic in Agentic Loop
    return result

def run_ra9_cognitive_engine(job_id: str, job_payload: Dict[str, Any]): # Modified signature
    """Main RA9 cognitive engine with enhanced CLI and reflection."""
    # cli = EnhancedCLI() # Removed
    # cli.show_welcome() # Removed
    print(json.dumps({"kind": "token", "agent": "system", "token": "RA9 Cognitive Engine Initializing..."}), flush=True)
    
    # Load RA9's persona
    ra9_persona = load_persona()
    print(json.dumps({"kind": "token", "agent": "system", "token": f"RA9's Identity Loaded: {ra9_persona['name']}"}), flush=True) # Changed to JSONL
    
    # Load user name from local memory on startup
    user_name = load_user_name_on_startup()
    if user_name != "User":
        print(json.dumps({"kind": "token", "agent": "system", "token": f"Welcome back, {user_name}!"}), flush=True) # Changed to JSONL

    # Initialize reflection engine
    reflection_engine = DynamicReflectionEngine()
    
    # Initialize recent memory summary (placeholder for now)
    recent_memory_summary = ""

    # No while True loop, process a single job_payload and exit
    try:
        # Get user query and other parameters from job_payload
        query = job_payload.get('text', '')
        mode = job_payload.get('mode', 'concise')
        loop_depth = job_payload.get('loopDepth', 1)
        allow_memory_write = job_payload.get('allowMemoryWrite', False)

        if not query:
            print(json.dumps({"kind": "error", "message": "No query received in job payload."}), flush=True)
            return # Exit if no query
            
        # Check for user context (name, etc.)
        context_type, context_value = check_user_context(query)
        if context_type == "name":
            store_user_info("name", context_value)
            print(json.dumps({"kind": "token", "agent": "system", "token": f"Nice to meet you, {context_value}!"}), flush=True) # Changed to JSONL
            
        # --- Input Layer (Perception): Classify input type, context integration, structured query ---
        print(json.dumps({"kind": "token", "agent": "system", "token": "Classifying query..."}), flush=True)
        # Consider passing 'mode' to classify_query if it influences classification
        structured_query = classify_query(query, memory_context=recent_memory_summary)
        print(json.dumps({"kind": "token", "agent": "system", "token": f"Query Classified: Intent: {structured_query.intent}, Type: {structured_query.query_type}, Confidence: {structured_query.confidence:.2f}"}), flush=True)
            
        # --- Meta-Classifier & Dispatcher (Mind's "Prefrontal Cortex") ---
        print(json.dumps({"kind": "token", "agent": "system", "token": "Dispatching query to cognitive agents..."}), flush=True)
        
        # --- Iteration Loop (controlled by loop_depth) ---
        all_iterations_results = [] # To store results of each iteration
        for current_iteration_index in range(loop_depth): # Loop for loop_depth
            print(json.dumps({"kind": "token", "agent": "system", "token": f"Starting iteration {current_iteration_index + 1}/{loop_depth} (Mode: {mode})..."}), flush=True)

            # Pass mode to dispatch_query_to_agents or use it here to influence agent selection
            processed_result = dispatch_query_to_agents(structured_query, ra9_persona)
            
            # Update variables based on processed_result
            final_answer = processed_result["final_answer"]
            iterations = processed_result["iterations"]
            quality_score = processed_result["quality_score"]
            agents_used = processed_result["agents_used"]

            # Analyze query complexity (still useful for display or other checks)
            complexity, reason = analyze_query_complexity(structured_query.content)
            print(json.dumps({"kind": "token", "agent": "system", "token": f"Complexity Analysis: {complexity} - {reason}"}), flush=True)
            
            # This block is now mostly for displaying results and storing memory
            estimated_time = 5 # Default estimated time, can be refined per agent
            if structured_query.query_type in ["strategic", "creative", "reflective"]:
                estimated_time = 10
            elif structured_query.query_type in ["logical", "emotional", "factual"]:
                estimated_time = 5

            # cli.show_processing_start(structured_query.query_type.capitalize() + " Processing", estimated_time) # Removed
            # cli.update_main_progress(50, estimated_time) # Removed

            # Simulate processing time based on estimated_time
            time.sleep(estimated_time * 0.5) # Simulate half the time here, rest after result

            # cli.update_main_progress(100, 0) # Removed
            # cli.cleanup() # Removed
            
            # cli.show_final_results( # Removed
            #     final_answer,
            #     iterations,
            #     quality_score,
            #     agents_used
            # ) # Removed

            # Emit tokens for the final answer
            for word in final_answer.split():
                print(json.dumps({"kind": "token", "agent": "actor", "token": word + " "}), flush=True)
            print(json.dumps({"kind": "token", "agent": "actor", "token": "\n"}), flush=True)

            # Emit iteration complete event
            iteration_id = f"{job_id}_iter_{current_iteration_index + 1}"
            # Create a more detailed iteration object to match the frontend's Iteration type
            iteration_obj = {
                "id": iteration_id,
                "iterationIndex": current_iteration_index + 1,
                "timestamp": datetime.now().isoformat(),
                "agentOutputs": [
                    {
                        "agentName": agents_used[0].lower().replace(" agent", ""), # e.g., "Logic Agent" -> "logical"
                        "text": final_answer,
                        "confidence": quality_score / 10.0, # Normalize to 0-1
                        "tokensRef": f"tokens_{current_iteration_index + 1}"
                    }
                ],
                "memoryHits": [], # Placeholder for now
                "citations": [], # Placeholder for now
                "verifier": {
                    "passed": False,
                    "score": 0.0,
                    "notes": ["Lightweight verifier not run in legacy engine path"]
                },
                "deltaSummary": f"Processed with {', '.join(agents_used)} in mode '{mode}'"
            }
            print(json.dumps({"kind": "iteration_complete", "iteration": iteration_obj}), flush=True)

            # Store memory (conditionally based on allow_memory_write)
            if allow_memory_write:
                store_memory(
                    structured_query.query_type, # Use the classified query type
                    structured_query.content,    # Use the extracted content
                    final_answer, # Use the final answer from the last iteration
                    f"Processed with {loop_depth} iterations, mode: {mode}, quality: {quality_score}/10",
                    "neutral"
                )
                print(json.dumps({"kind": "token", "agent": "system", "token": "Memory stored."}), flush=True)
            else:
                print(json.dumps({"kind": "token", "agent": "system", "token": "Memory write skipped (allowMemoryWrite is false)."}), flush=True)
            
            # Show learning improvements if any
            if processed_result.get("learning_improvements"):
                print(json.dumps({"kind": "token", "agent": "system", "token": "🧠 LEARNING INSIGHTS:"}), flush=True)
                for improvement in processed_result["learning_improvements"][-3:]:  # Show last 3
                    print(json.dumps({"kind": "token", "agent": "system", "token": f"• {improvement}"}), flush=True)
        
    except KeyboardInterrupt:
        print(json.dumps({"kind": "token", "agent": "system", "token": "Processing interrupted by user."}), flush=True)
    except Exception as e:
        print(json.dumps({"kind": "error", "message": f"An unexpected error occurred during cognitive engine run: {str(e)}"}), flush=True)
    finally:
        print(json.dumps({"kind": "done"}), flush=True) # Emit done after processing a single job

def recursive_thinking_loop(query: str, agents: list, max_iterations: int = 5) -> Dict[str, Any]:
    """Legacy recursive thinking loop - kept for compatibility."""
    print(json.dumps({"kind": "token", "agent": "system", "token": "⚠️  Using legacy recursive thinking loop"}), flush=True)
    # Implementation would go here
    return {"final_answer": "Legacy processing", "iterations": 1, "quality_score": 5.0}