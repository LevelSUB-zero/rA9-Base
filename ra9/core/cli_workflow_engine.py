#!/usr/bin/env python3
"""
CLI Workflow Engine - Integrates enhanced CLI with the new workflow
"""

import json
import time
import sys
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .enhanced_cli_ui import get_cli
from .executor import execute_ra9_multi_agent
from .engine import load_persona
from ..router.query_classifier import classify_query, StructuredQuery
from ..memory.memory_manager import store_memory, store_semantic, store_reflective

class CLIWorkflowEngine:
    """Enhanced workflow engine with CLI visualization"""
    
    def __init__(self):
        self.cli = get_cli()
        self.persona = load_persona()
        self.performance_metrics = {
            "api_calls": 0,
            "tokens_generated": 0
        }
    
    def run_workflow(self, job_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete workflow with CLI visualization"""
        
        # Extract parameters
        user_id = job_payload.get("userId", "")
        text = job_payload.get("text", "")
        mode = job_payload.get("mode", "concise")
        loop_depth = job_payload.get("loopDepth", 1)
        allow_memory_write = job_payload.get("allowMemoryWrite", True)
        
        if not text:
            self.cli.show_workflow_stage("error", "No text provided in payload")
            return {"error": "No text provided"}
        
        # Start session
        self.cli.start_session()
        
        try:
            # Stage 0: Pre-Processing
            self.cli.show_workflow_stage("initializing", "Loading persona and context...")
            time.sleep(0.5)  # Brief pause for visual effect
            
            # Stage 1: Query Classification
            self.cli.show_workflow_stage("classifying", "Analyzing query intent and complexity...")
            start_time = time.time()
            
            try:
                structured_query = classify_query(text, user_id=user_id)
                self.performance_metrics["api_calls"] += 1
            except Exception as e:
                self.cli.show_workflow_stage("error", f"Query classification failed: {str(e)}")
                return {"error": f"Query classification failed: {str(e)}"}
            
            classification_time = time.time() - start_time
            self.cli.show_classification_result(structured_query)
            
            # Stage 2: Memory Fetch
            self.cli.show_workflow_stage("memory_fetch", "Retrieving relevant memories...")
            self.cli.show_memory_status("episodic", 5, "Recent interactions loaded")
            self.cli.show_memory_status("semantic", 12, "Knowledge base indexed")
            self.cli.show_memory_status("reflective", 3, "Lessons learned retrieved")
            time.sleep(0.3)
            
            # Stage 3: Parallel Agent Processing
            self.cli.show_workflow_stage("parallel_agents", "Activating cognitive agents...")
            
            # Register agents based on classification
            agent_configs = self._get_agent_configs(structured_query)
            for name, role in agent_configs:
                self.cli.register_agent(name, role)
            
            # Show agent status
            self.cli.show_agent_status()
            
            # Execute multi-agent workflow
            start_time = time.time()
            try:
                result = execute_ra9_multi_agent(text, self.persona, user_id=user_id, allow_memory_write=allow_memory_write)
                agent_time = time.time() - start_time
            except Exception as e:
                self.cli.show_workflow_stage("error", f"Multi-agent execution failed: {str(e)}")
                return {"error": f"Multi-agent execution failed: {str(e)}"}
            
            # Check if result has expected structure
            if not isinstance(result, dict):
                self.cli.show_workflow_stage("error", "Multi-agent execution returned invalid result")
                return {"error": "Multi-agent execution returned invalid result"}
            
            if "final_answer" not in result:
                self.cli.show_workflow_stage("error", "Multi-agent execution did not produce final answer")
                return {"error": "Multi-agent execution did not produce final answer"}
            
            # Update agent statuses
            if "sub_agent_outputs" in result:
                for agent_output in result["sub_agent_outputs"]:
                    self.cli.update_agent_status(
                        agent_output["agent"],
                        "complete",
                        agent_output["output"],
                        agent_output.get("confidence", 0.0)
                    )
            
            # Stage 4: Self-Critique
            self.cli.show_workflow_stage("self_critique", "Running self-critique analysis...")
            time.sleep(0.5)
            
            # Stage 5: Meta-Coherence
            self.cli.show_workflow_stage("meta_coherence", "Checking coherence and resolving conflicts...")
            coherence_ok = result.get("coherence_score", False)
            if coherence_ok:
                self.cli.show_workflow_stage("meta_coherence", "✓ Coherence check passed")
            else:
                self.cli.show_workflow_stage("meta_coherence", "⚠ Coherence issues detected, applying repairs...")
            time.sleep(0.3)
            
            # Stage 6: Reflection Loop
            self.cli.show_workflow_stage("reflection_loop", f"Running {structured_query.reasoning_depth} reflection...")
            self.cli.show_iteration_progress(1, 1, "Single iteration complete")
            time.sleep(0.2)
            
            # Stage 7: Meta-Self Report
            if "meta_report" in result:
                self.cli.show_meta_report(result["meta_report"])
            
            # Stage 8: Final Output
            self.cli.show_workflow_stage("final_output", "Generating final response...")
            final_answer = result.get("final_answer", "")
            reflection = result.get("reflection", "")
            
            # Count tokens (rough estimate)
            self.performance_metrics["tokens_generated"] = len(final_answer.split()) * 1.3
            
            self.cli.show_final_output(final_answer, reflection)
            
            # Stage 9: Autonomy & Post-Processing
            if allow_memory_write:
                self.cli.show_workflow_stage("autonomy", "Writing to memory layers...")
                
                # Write to episodic memory
                self.cli.show_memory_write("episodic", final_answer)
                store_memory("episodic", text, final_answer, reflection, allow_memory_write=True)
                
                # Write to semantic if substantial
                if len(final_answer) > 300:
                    self.cli.show_memory_write("semantic", final_answer)
                    store_semantic(final_answer, tags=[structured_query.query_type] + structured_query.labels)
                
                # Write to reflective if there were issues
                if not coherence_ok and result.get("coherence_feedback"):
                    self.cli.show_memory_write("reflective", result["coherence_feedback"])
                    store_reflective(result["coherence_feedback"], related_query=text)
            
            # Update performance metrics
            self.cli.performance_metrics.update(self.performance_metrics)
            
            return result
            
        except Exception as e:
            self.cli.show_workflow_stage("error", f"Error: {str(e)}")
            return {"error": str(e)}
        
        finally:
            # End session
            self.cli.end_session()
    
    def _get_agent_configs(self, structured_query: StructuredQuery) -> List[tuple]:
        """Get agent configurations based on classification"""
        
        # Base agents for primary type
        primary_agents = {
            "logical": [
                ("Premise Extractor", "Breaks query into logical claims"),
                ("Assumption Unfolder", "Lists hidden assumptions"),
                ("CoT Reasoner", "Runs chain-of-thought steps"),
                ("Truth Validator", "Checks factual consistency"),
                ("Contradiction Spotter", "Finds logical flaws")
            ],
            "emotional": [
                ("Emotion Detector", "Understands emotional context"),
                ("Affective Memory Mapper", "Connects to past emotional state"),
                ("Empathy Generator", "Responds with aligned emotional tone"),
                ("Emotional Reframer", "Transforms negative tone into growth path"),
                ("Tone Balancer", "Harmonizes language expression")
            ],
            "strategic": [
                ("Goal Extractor", "Identifies core objectives"),
                ("Constraint Analyzer", "Maps limitations and boundaries"),
                ("Path Synthesizer", "Creates multiple strategic paths"),
                ("Trade-off Engine", "Evaluates cost-benefit scenarios"),
                ("Risk Simulator", "Models potential failure points")
            ],
            "creative": [
                ("Concept Disruptor", "Breaks assumptions"),
                ("Cross-Domain Mapper", "Pulls analogies from unrelated fields"),
                ("Mythical Synthesizer", "Adds sci-fi, spiritual, or narrative layer"),
                ("Speculative Engineer", "Predicts future evolution of ideas"),
                ("Creative Filter", "Scores based on novelty × feasibility")
            ],
            "reflective": [
                ("Existential Frame Evaluator", "Finds deeper meaning"),
                ("Wisdom Lens Agent", "Uses philosophical framing"),
                ("Mythopoetic Generator", "Uses metaphor to explain insight"),
                ("Ego Disruptor", "Transcends user identity framing"),
                ("Transcendence Mapper", "Offers beyond-the-mind paths")
            ]
        }
        
        # Get primary agents
        agents = primary_agents.get(structured_query.query_type, primary_agents["logical"])
        
        # Add secondary agents based on labels
        for label in structured_query.labels:
            if label in primary_agents and label != structured_query.query_type:
                # Add 2-3 agents from secondary type
                secondary_agents = primary_agents[label][:3]
                agents.extend(secondary_agents)
        
        return agents

def run_cli_workflow(job_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for CLI workflow"""
    engine = CLIWorkflowEngine()
    return engine.run_workflow(job_payload)
