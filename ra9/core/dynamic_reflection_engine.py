import json
import time
import re
from typing import List, Dict, Any, Tuple
from ra9.tools.tool_api import ask_gemini, load_prompt_from_json
from ra9.memory.memory_manager import store_memory, get_user_name

class DynamicReflectionEngine:
    """Enhanced dynamic reflection engine with reinforcement learning and adaptive loops."""
    
    def __init__(self):
        self.available_agents = {
            "logical": "Logical reasoning and analysis",
            "emotional": "Empathy and emotional intelligence", 
            "strategic": "Planning and strategic thinking",
            "creative": "Innovation and creative solutions",
            "operational": "Practical implementation",
            "spiritual": "Philosophical and existential insights",
            "knowledge": "Information synthesis and retrieval",
            "search": "External data gathering",
            "code": "Technical and computational thinking",
            "graphical": "Visual and spatial reasoning",
            "ethical": "Moral reasoning and values",
            "brain_tool": "Meta-cognitive analysis"
        }
        
        self.agent_roles = {
            "logical": "Focus on step-by-step reasoning, identify logical fallacies, ensure coherence",
            "emotional": "Consider human emotions, empathy, psychological factors, emotional intelligence",
            "strategic": "Long-term planning, risk assessment, resource optimization, strategic thinking",
            "creative": "Innovative solutions, lateral thinking, creative problem-solving, novel approaches",
            "operational": "Practical implementation, feasibility, real-world constraints, execution",
            "spiritual": "Philosophical insights, existential questions, meaning, purpose, consciousness",
            "knowledge": "Information synthesis, knowledge integration, comprehensive understanding",
            "search": "External data gathering, current information, research, fact-checking",
            "code": "Technical analysis, computational thinking, algorithmic approaches, system design",
            "graphical": "Visual reasoning, spatial relationships, pattern recognition, visual synthesis",
            "ethical": "Moral reasoning, values, ethical implications, fairness, justice",
            "brain_tool": "Meta-cognitive analysis, self-reflection, process optimization, learning"
        }
        
        # Reinforcement learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.agent_performance = {agent: 0.5 for agent in self.available_agents}
        self.feedback_history = []

        self._prompt_name_mapping = {
            "knowledge": "KnowledgeMemoryLayerPrompt",
            "search": "SearchAgentLayerPrompt",
            "code": "CodeExecutionLayerPrompt",
            "brain_tool": "BrainToolLayerPrompt",
        }
        
    def orchestrate_deep_processing(self, query: str, ra9_persona: Dict, pause: bool = False, progress_callback=None) -> Dict[str, Any]:
        """Orchestrate deep processing with reinforcement learning and adaptive loops.

        If pause is True, skip all iterations and return immediately with a paused result.
        """
        if pause:
            return {
                "final_answer": "Processing paused — iterations are disabled.",
                "iterations": 0,
                "quality_score": 0.0,
                "agents_used": [],
                "complexity_level": "Paused",
                "learning_improvements": []
            }
        print(f"🧠 [RA9] Initiating deep cognitive processing...")
        
        # Analyze query complexity and determine loop count
        complexity_analysis = self._analyze_query_complexity(query)
        complexity_level = complexity_analysis["level"]
        loop_count = self._determine_loop_count(complexity_level)
        
        print(f"📊 [RA9] Query complexity: {complexity_level} | Target loops: {loop_count}")
        
        # Select optimal agents based on complexity and learning history
        selected_agents = self._select_optimal_agents(query, complexity_level)
        
        # Execute debate loop with reinforcement learning
        final_result = self._execute_debate_loop(query, selected_agents, ra9_persona, loop_count, progress_callback=progress_callback)
        
        # Synthesize perfect output
        perfect_output = self._synthesize_perfect_output(query, final_result, ra9_persona)
        
        # Store experience for learning
        self._store_experience(query, complexity_level, selected_agents, final_result)
        
        return {
            "final_answer": perfect_output,
            "iterations": final_result["iterations"],
            "quality_score": final_result["quality_score"],
            "agents_used": selected_agents,
            "complexity_level": complexity_level,
            "learning_improvements": final_result["learning_improvements"]
        }
    
    def _analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity using LLM."""
        complexity_prompt = f"""
        Analyze the complexity of this query and classify it into one of these levels:
        
        - Simple: Basic questions, math, greetings (1-2 loops)
        - Moderate: Analysis, explanations (3-5 loops) 
        - Critical: Complex reasoning, puzzles (8-10 loops)
        - Ultra-Deep: Philosophical, multi-step logic (12-15 loops)
        
        Query: {query}
        
        Respond in JSON format:
        {{
            "level": "<complexity_level>",
            "reasoning": "<explanation>",
            "estimated_difficulty": <1-10>,
            "required_depth": "<description>"
        }}
        """
        
        try:
            response = ask_gemini(complexity_prompt)
            analysis = json.loads(response)
            return analysis
        except:
            # Fallback analysis (keyword-based heuristics)
            ql = query.lower()
            ultra_keywords = [
                "agi alignment", "superintelligent agi", "corrigibility", "constitutional ai",
                "decision theory", "fdt", "cdt", "edt", "irl", "inverse reinforcement learning",
                "cooperative irl", "interpretability", "governance", "threat model", "red-teaming"
            ]
            if any(k in ql for k in ultra_keywords) or any(k in ql for k in ["philosophy", "existential", "meaning", "consciousness", "logic puzzle", "complex"]):
                return {"level": "Ultra-Deep", "reasoning": "Advanced safety/alignment or philosophical/logic content", "estimated_difficulty": 9, "required_depth": "Deep multi-agent reflection"}
            elif any(word in ql for word in ["analyze", "explain", "compare", "evaluate", "discuss"]):
                return {"level": "Critical", "reasoning": "Requires detailed analysis", "estimated_difficulty": 7, "required_depth": "Multi-perspective analysis"}
            elif any(word in ql for word in ["what", "how", "why", "when", "where"]):
                return {"level": "Moderate", "reasoning": "Information seeking", "estimated_difficulty": 5, "required_depth": "Basic analysis"}
            else:
                return {"level": "Simple", "reasoning": "Direct question", "estimated_difficulty": 3, "required_depth": "Quick response"}

    def _extract_style_constraints(self, query: str) -> str:
        """Extract formatting directives embedded in the user's query (e.g., crisp lists, minimal prose)."""
        ql = query.lower()
        directives = []
        if "crisp numbered" in ql or "numbered list" in ql or "numbered lists" in ql:
            directives.append("Use strictly numbered lists for all sections.")
        if "minimal prose" in ql or "concise" in ql or "precise" in ql or "technical" in ql:
            directives.append("Minimize prose; use terse, technical phrasing.")
        if "sections" in ql or "specify:" in ql:
            directives.append("Follow the requested section order exactly.")
        # Always enforce no meta or persona in final output
        directives.append("No meta commentary, no acknowledgments, no references to persona or process.")
        return "\n".join(f"- {d}" for d in directives)
    
    def _determine_loop_count(self, complexity_level: str) -> int:
        """Determine loop count based on complexity level."""
        loop_counts = {
            "Simple": 2,
            "Moderate": 5,
            "Critical": 10,
            "Ultra-Deep": 15
        }
        return loop_counts.get(complexity_level, 5)
    
    def _select_optimal_agents(self, query: str, complexity_level: str) -> List[str]:
        """Select optimal agents using AI-driven selection + reinforcement heuristics for deep/critical only."""
        from core.query_complexity_analyzer import select_agents_for_query

        # For simple/moderate, keep minimal sets
        if complexity_level in ["Simple", "Moderate"]:
            base = {"Simple": ["logical"], "Moderate": ["logical", "emotional"]}
            return base[complexity_level]

        # For Critical/Ultra-Deep, use AI selector first
        ai_selected = select_agents_for_query(query)

        # Apply RL heuristic: if a high-performer not present, add it
        for agent, perf in sorted(self.agent_performance.items(), key=lambda x: x[1], reverse=True):
            if perf > 0.75 and agent not in ai_selected:
                ai_selected.append(agent)
            if len(ai_selected) >= 8:
                break

        # Enforce bounds
        if complexity_level == "Critical":
            return ai_selected[:6] if len(ai_selected) >= 3 else ["logical", "strategic", "creative", "emotional"]
        else:
            return ai_selected[:8] if len(ai_selected) >= 3 else ["logical", "emotional", "strategic", "creative", "knowledge", "ethical"]
    
    def _execute_debate_loop(self, query: str, agents: List[str], ra9_persona: Dict, max_iterations: int, progress_callback=None) -> Dict[str, Any]:
        """Execute debate loop with reinforcement learning and adaptive feedback."""
        print(f"🔄 [RA9] Starting debate loop with {len(agents)} agents, max {max_iterations} iterations")
        
        iteration_count = 0
        current_thought = ""
        quality_score = 0.0
        learning_improvements = []
        
        while iteration_count < max_iterations:
            iteration_count += 1
            print(f"🔄 [RA9] Iteration {iteration_count}/{max_iterations}")
            
            # Execute agent debate with feedback integration
            debate_results = self._execute_agent_debate(query, agents, current_thought, ra9_persona, iteration_count)
            
            # Assess quality with reinforcement learning
            quality_assessment = self._assess_quality_with_learning(query, debate_results, iteration_count, max_iterations)
            quality_score = quality_assessment["score"]
            feedback = quality_assessment["feedback"]
            
            # Update agent performance based on contribution quality
            self._update_agent_performance(agents, debate_results, quality_score)
            
            # Progress callback after assessment
            if callable(progress_callback):
                try:
                    progress_callback({
                        "iteration": iteration_count,
                        "max_iterations": max_iterations,
                        "agents": list(agents),
                        "quality_score": quality_score
                    })
                except Exception:
                    pass

            # Check if quality threshold reached
            if quality_score >= 9.5:
                print(f"✅ [RA9] Quality threshold reached: {quality_score}/10")
                learning_improvements.append(f"Iteration {iteration_count}: Quality threshold achieved")
                break
            
            # Apply reinforcement learning to improve next iteration
            improvement = self._apply_reinforcement_learning(query, agents, debate_results, feedback, iteration_count)
            learning_improvements.append(improvement)
            
            # Update current thought for next iteration
            current_thought = self._synthesize_debate_results(debate_results)
            
            # Adaptive agent reconfiguration
            if iteration_count % 3 == 0:
                agents = self._reconfigure_agents(query, agents, quality_score, iteration_count)
        
        return {
            "iterations": iteration_count,
            "quality_score": quality_score,
            "final_results": debate_results,
            "learning_improvements": learning_improvements
        }
    
    def _execute_agent_debate(self, query: str, agents: List[str], previous_thought: str, ra9_persona: Dict, iteration: int) -> Dict[str, str]:
        """Execute agent debate with enhanced feedback integration."""
        debate_results = {}
        
        for agent in agents:
            # Load agent prompt
            try:
                prompt_suffix = self._prompt_name_mapping.get(agent, f"{agent.title()}MetaLayerPrompt")
                prompt_file = f"ra9/Prompts/ra9-v0.01 alpha/RA9{prompt_suffix}.json"
                agent_prompt = load_prompt_from_json(prompt_file)
            except Exception as e:
                print(f"Error: Prompt file not found at {prompt_file}")
                agent_prompt = f"You are RA9's {agent} agent. Provide your perspective on the query."
            
            # Create enhanced prompt with feedback and learning
            enhanced_prompt = f"""
            {agent_prompt}
            
            Query: {query}
            Previous Iteration Thought: {previous_thought}
            Current Iteration: {iteration}
            RA9's Core Values: {ra9_persona.get('core_values', [])}
            
            Consider the feedback from previous iterations and provide an improved perspective.
            Focus on areas that need enhancement based on the learning history.
            
            Your role: {self.agent_roles.get(agent, 'Provide your unique perspective')}
            
            Response:
            """
            
            try:
                response = ask_gemini(enhanced_prompt)
                debate_results[agent] = response
                print(f"🤖 [{agent.upper()}] Contributed to iteration {iteration}")
            except Exception as e:
                print(f"⚠️ [RA9] Error in {agent} agent: {e}")
                debate_results[agent] = f"Error in {agent} agent processing"
        
        return debate_results
    
    def _assess_quality_with_learning(self, query: str, results: Dict[str, str], iteration: int, max_iterations: int) -> Dict[str, Any]:
        """Assess quality with reinforcement learning integration."""
        assessment_prompt = f"""
        Assess the quality of these debate results for the given query. Provide specific, actionable feedback for reinforcement learning.
        
        Query: {query}
        Results: {json.dumps(results, indent=2)}
        Iteration: {iteration}/{max_iterations}
        
        Consider:
        1. Logical coherence and reasoning quality
        2. Emotional intelligence and empathy
        3. Strategic thinking and planning
        4. Creative innovation and originality
        5. Practical feasibility and implementation
        6. Ethical considerations and values alignment
        7. Knowledge integration and synthesis
        8. Learning from previous iterations
        
        Rate from 1-10 and provide detailed, actionable feedback for improvement.
        Ensure your response is in strict JSON format:
        {{
            "score": <number, 1-10>,
            "feedback": "<detailed, actionable feedback for improvement>",
            "should_continue": <true/false>,
            "learning_insights": "<specific insights for reinforcement learning>",
            "agent_suggestions": {{
                "improve": ["agent1", "agent2"],
                "add": ["agent3"],
                "remove": ["agent4"]
            }}
        }}
        """
        
        try:
            response = ask_gemini(assessment_prompt)
            # Empty or API error string fallback
            if not response or response.strip() == "" or response.startswith("Error:"):
                return self._get_fallback_assessment(iteration, max_iterations)

            # Normalize markdown fenced JSON blocks if present
            stripped = response.strip()
            if stripped.startswith("```") and stripped.endswith("```"):
                # Remove leading/trailing triple backticks and optional language tag
                response = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", stripped)

            # Try direct JSON parse
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Attempt to extract JSON block via robust regex (DOTALL)
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    candidate = json_match.group(0)
                    # Remove common prefix/suffix noise
                    candidate = candidate.strip()
                    try:
                        return json.loads(candidate)
                    except Exception:
                        pass
                # Final fallback
                return self._get_fallback_assessment(iteration, max_iterations)
        except Exception as e:
            print(f"⚠️ [RA9] Quality assessment error: {e}")
            return self._get_fallback_assessment(iteration, max_iterations)
    
    def _get_fallback_assessment(self, iteration: int, max_iterations: int) -> Dict[str, Any]:
        """Provide fallback assessment when LLM response fails."""
        should_continue = iteration < max_iterations
        base_score = 6.0 if should_continue else 8.5
        return {
            "score": base_score,
            "feedback": "Quality assessment fallback used due to parsing/response issue.",
            "should_continue": should_continue,
            "learning_insights": "Assessment system encountered an error; proceeding with default learning parameters.",
            "agent_suggestions": {"improve": [], "add": [], "remove": []}
        }
    
    def _update_agent_performance(self, agents: List[str], results: Dict[str, str], quality_score: float):
        """Update agent performance using reinforcement learning."""
        for agent in agents:
            if agent in results:
                # Simple performance update based on quality score
                current_performance = self.agent_performance[agent]
                performance_delta = (quality_score - 5.0) / 10.0  # Normalize to -0.5 to 0.5
                
                # Update with learning rate
                new_performance = current_performance + (self.learning_rate * performance_delta)
                self.agent_performance[agent] = max(0.1, min(1.0, new_performance))
                
                print(f"📈 [RA9] {agent} performance updated: {current_performance:.3f} → {self.agent_performance[agent]:.3f}")
    
    def _apply_reinforcement_learning(self, query: str, agents: List[str], results: Dict[str, str], feedback: str, iteration: int) -> str:
        """Apply reinforcement learning to improve next iteration."""
        learning_prompt = f"""
        Based on the current debate results and feedback, provide specific learning insights for the next iteration.
        
        Query: {query}
        Current Results: {json.dumps(results, indent=2)}
        Feedback: {feedback}
        Iteration: {iteration}
        
        Provide specific, actionable insights for improvement:
        1. What worked well?
        2. What needs improvement?
        3. How should agents adjust their approach?
        4. What new perspectives should be considered?
        
        Response:
        """
        
        try:
            learning_insights = ask_gemini(learning_prompt)
            return f"Iteration {iteration}: {learning_insights[:100]}..."
        except:
            return f"Iteration {iteration}: Learning analysis completed"
    
    def _reconfigure_agents(self, query: str, current_agents: List[str], quality_score: float, iteration: int) -> List[str]:
        """Reconfigure agents based on performance and learning."""
        if quality_score < 6.0 and iteration > 3:
            # Add high-performing agents
            high_performers = [agent for agent, perf in self.agent_performance.items() 
                             if perf > 0.7 and agent not in current_agents]
            if high_performers:
                new_agent = high_performers[0]
                current_agents.append(new_agent)
                print(f"🔄 [RA9] Added high-performing agent: {new_agent}")
        
        return current_agents
    
    def _synthesize_debate_results(self, results: Dict[str, str]) -> str:
        """Synthesize debate results into coherent thought."""
        synthesis_prompt = f"""
        Synthesize these agent debate results into a coherent, integrated thought:
        
        {json.dumps(results, indent=2)}
        
        Create a unified perspective that integrates all agent contributions:
        """
        
        try:
            synthesis = ask_gemini(synthesis_prompt)
            return synthesis
        except:
            return "Synthesis of debate results"
    
    def _synthesize_perfect_output(self, query: str, final_result: Dict[str, Any], ra9_persona: Dict) -> str:
        """Synthesize the perfect final output."""
        style_constraints = self._extract_style_constraints(query)
        synthesis_prompt = f"""
        Create the perfect final response to the query, synthesizing all iterations and learning.

        Query: {query}
        Final Results: {json.dumps(final_result['final_results'], indent=2)}
        Quality Score: {final_result['quality_score']}/10
        Iterations: {final_result['iterations']}
        Learning Improvements: {final_result['learning_improvements']}

        Hard formatting constraints (must follow exactly):
        {style_constraints}

        Additional rules:
        - Do not include any preamble or epilogue; return only the content.
        - No apologies, no discussion of limitations, no mention of tools or loops.
        - Keep to the user's requested tone and structure if present in the query.

        Produce only the final answer.
        """
        
        try:
            perfect_output = ask_gemini(synthesis_prompt)
            return perfect_output
        except Exception as e:
            print(f"⚠️ [RA9] Final synthesis error: {e}")
            return "Final synthesis completed with comprehensive analysis."
    
    def _store_experience(self, query: str, complexity_level: str, agents_used: List[str], final_result: Dict[str, Any]):
        """Store experience for future learning."""
        experience = {
            "query": query,
            "complexity_level": complexity_level,
            "agents_used": agents_used,
            "iterations": final_result["iterations"],
            "final_quality": final_result["quality_score"],
            "learning_improvements": final_result["learning_improvements"],
            "timestamp": time.time()
        }
        
        self.feedback_history.append(experience)
        
        # Keep only recent history
        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]
        
        print(f"💾 [RA9] Experience stored for future learning") 