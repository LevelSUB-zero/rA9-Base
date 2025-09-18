import json
import time
from typing import List, Dict, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from ra9.tools.tool_api import ask_gemini, load_prompt_from_json
from ra9.core.reflective import reflect_response
from ra9.core.framer import frame_output
from ra9.memory.memory_manager import store_memory

class RA9MultiAgentExecutor:
    """Orchestrates the multi-agent cognitive architecture with recursive loops."""
    
    def __init__(self):
        self.meta_layers = {
            "logical": "RA9LogicalMetaLayerPrompt.json",
            "emotional": "RA9EmotionalMetaLayerPrompt.json", 
            "strategic": "RA9StrategicMetaLayerPrompt.json",
            "creative": "RA9CreativeMetaLayerPrompt.json",
            "operational": "RA9OperationalMetaLayerPrompt.json",
            "spiritual": "spiritual_meta_layer.json"
        }
        
    def execute_agent_layer(self, query: str, classification: str, ra9_persona: Dict, reasoning_depth: str = "auto") -> Dict[str, Any]:
        """Execute a meta-layer with multiple sub-agents in recursive loops."""
        
        # Load the appropriate meta-layer prompt
        layer_prompt_file = self.meta_layers.get(classification, "RA9LogicalMetaLayerPrompt.json")
        layer_prompt = load_prompt_from_json(f"ra9/Prompts/ra9-v0.01 alpha/{layer_prompt_file}")
        
        # Determine number of sub-agents based on layer type
        sub_agent_configs = self._get_sub_agent_config(classification)
        
        print(f"🧠 Executing {classification.upper()} Meta-Layer with {len(sub_agent_configs)} sub-agents...")
        
        # Determine rounds from depth (reduced to avoid rate limits)
        if reasoning_depth == "shallow":
            iteration_rounds = 1
        elif reasoning_depth == "deep":
            iteration_rounds = 2  # Reduced from 3
        else:
            iteration_rounds = 1  # Reduced from 2

        # Phase 1: Multi-sub-agent generation with ITERATIVE LOOPS
        sub_agent_outputs = []
        
        for round_num in range(iteration_rounds):
            print(f"\n🔄 ROUND {round_num + 1}: Sub-Agent Debate & Refinement")
            
            if round_num == 0:
                # First round: Initial thoughts from each sub-agent (sequential to avoid rate limits)
                for i, (agent_name, agent_role) in enumerate(sub_agent_configs):
                    print(f"  🧠 Sub-Agent {i+1}: {agent_name} ({agent_role})")
                    sub_prompt = self._create_sub_agent_prompt(layer_prompt, agent_name, agent_role, query)
                    
                    # Add delay between API calls to avoid rate limiting
                    if i > 0:
                        time.sleep(2)  # 2 second delay between calls
                    
                    response = ask_gemini(sub_prompt)
                    print(f"    💭 {agent_name}: {response[:100]}...")
                    sub_agent_outputs.append({
                        "agent": agent_name,
                        "role": agent_role,
                        "output": response,
                        "confidence": self._estimate_confidence(response),
                        "round": round_num + 1
                    })
            else:
                # Second round: Agents refine based on others' thoughts (simplified)
                print(f"  🔄 Refining thoughts based on previous round...")
                
                # Get previous round's insights (simplified to avoid too many API calls)
                prev_insights = "\n".join([
                    f"{output['agent']}: {output['output'][:150]}..."
                    for output in sub_agent_outputs if output['round'] == round_num
                ])
                
                # Each agent gets to refine their thinking
                for i, (agent_name, agent_role) in enumerate(sub_agent_configs):
                    print(f"  🧠 Sub-Agent {i+1}: {agent_name} (Refining)")
                    
                    refinement_prompt = f"""
{layer_prompt}

You are the **{agent_name}** sub-agent with the role: **{agent_role}**

Previous round insights from other agents:
{prev_insights}

Query: {query}

Instructions:
- Review the insights from other agents
- Refine your thinking based on their perspectives
- Provide an improved, more nuanced analysis
- Focus on your specific role: {agent_role}
- Keep it concise (2-3 sentences)

How do you refine your analysis considering the other agents' thoughts?
"""
                    
                    refined_response = ask_gemini(refinement_prompt)
                    print(f"    💭 {agent_name} (refined): {refined_response[:100]}...")
                    
                    sub_agent_outputs.append({
                        "agent": agent_name,
                        "role": agent_role,
                        "output": refined_response,
                        "confidence": self._estimate_confidence(refined_response),
                        "round": round_num + 1
                    })
        
        # Phase 2: Self-critique pass (basic)
        critique_prompt = f"""
You are the Self-Critique Layer. Review each sub-agent's output for contradictions, vagueness, or missing evidence.
For each item, return a brief improved rewrite if needed.

Sub-Agent Outputs:
{json.dumps([{k: v for k, v in o.items() if k in ['agent','role','output','confidence','round']} for o in sub_agent_outputs], ensure_ascii=False)}

Return a concise improved synthesis paragraph.
"""
        critique_response = ask_gemini(critique_prompt)
        
        # Phase 2.5: Emotional/Existential Layer Check
        print(f"\n💭 Running emotional/existential analysis...")
        emotional_prompt = f"""
        You are RA9's Emotional/Existential Layer. Your role is to examine the human consequences and emotional weight of the reasoning so far.
        
        Query: "{query}"
        Current reasoning from {len(sub_agent_outputs)} agents has been processed.
        
        Ask yourself:
        1. What is the emotional weight or human consequence of this reasoning?
        2. How might this answer affect someone's life, decisions, or worldview?
        3. What existential or spiritual dimensions are we missing?
        4. Is this reasoning too sterile or detached from human experience?
        
        Provide a brief emotional/existential assessment and suggest any adjustments needed to make the reasoning more human-centered:
        """
        
        emotional_analysis = ask_gemini(emotional_prompt)
        print(f"  💭 Emotional analysis: {emotional_analysis[:100]}...")

        # Phase 3: Feedback Aggregation (intent-weight hint)
        print(f"\n🔄 Aggregating feedback from {len(sub_agent_outputs)} sub-agent outputs across {iteration_rounds} rounds...")
        intent_weight_hint = f"Primary intent: {classification}. Weight {classification} perspectives more heavily."
        emotional_hint = f"Emotional/Existential considerations: {emotional_analysis}"
        aggregated_seed = self._aggregate_feedback(sub_agent_outputs + [
            {"agent": "meta", "role": "intent_weight", "output": intent_weight_hint, "round": 1},
            {"agent": "emotional", "role": "human_consequence", "output": emotional_hint, "round": 1}
        ], query, ra9_persona)
        aggregated_output = f"{aggregated_seed}\n\nRefinements from self-critique: {critique_response}\n\nEmotional/Existential insights: {emotional_analysis}"
        
        # Phase 4: Iterative Reflective Processing (narrative style)
        print(f"🔄 Running iterative reflection...")
        reflection_prompt = f"""
        You are RA9's Iterative Reflection Layer. Instead of just evaluating, narrate your thinking process as you review the reasoning.
        
        Query: "{query}"
        Current reasoning: "{aggregated_output[:500]}..."
        
        Narrate your reflection process like this:
        "I see [specific observation about the reasoning]. This makes me think [your analysis]. 
        I notice a potential issue: [specific concern]. So I'll adjust my approach by [specific change].
        Actually, let me reconsider [specific aspect] because [reasoning]."
        
        Make this feel like natural, iterative thinking rather than final evaluation.
        """
        
        iterative_reflection = ask_gemini(reflection_prompt)
        print(f"  🔄 Iterative reflection: {iterative_reflection[:100]}...")
        
        # Phase 5: Meta-Coherence Check
        print(f"🔄 Checking meta-coherence...")
        is_coherent, coherence_feedback = self._check_meta_coherence(aggregated_output, sub_agent_outputs, ra9_persona)
        
        # Optional recursion if incoherent and depth allows
        if not is_coherent and iteration_rounds > 1:
            repair_prompt = f"""
Meta-coherence feedback:
{coherence_feedback}

I see a flaw in my reasoning, so I'll adjust my plan like this: [specific improvement based on the feedback]
"""
            repair = ask_gemini(repair_prompt)
            aggregated_output = f"{aggregated_output}\n\nIterative adjustment: {repair}"

        # Phase 5.5: Example Generation Pass
        print(f"🔄 Generating concrete examples...")
        example_prompt = f"""
        You are RA9's Example Generation Layer. Your role is to ground abstract reasoning in concrete, relatable examples.
        
        Query: "{query}"
        Current reasoning: "{aggregated_output[:500]}..."
        
        Generate 1-2 concrete examples that illustrate the key points. Make them:
        1. Relatable to everyday human experience
        2. Specific and vivid (not generic)
        3. Directly connected to the main reasoning
        4. Helpful for understanding the concepts
        
        Provide your examples:
        """
        
        examples = ask_gemini(example_prompt)
        print(f"  📝 Examples generated: {examples[:100]}...")
        
        # Phase 6: Final Framing
        print(f"🔄 Applying final framing...")
        final_output = frame_output(aggregated_output, classification)
        
        # Add examples and iterative reflection to final output
        final_output = f"{final_output}\n\n🔄 Iterative Reflection:\n{iterative_reflection}\n\n📝 Concrete Examples:\n{examples}"

        # Phase 6.5: Confidence & Next-Step Logging
        print(f"🔄 Generating confidence assessment and next steps...")
        confidence_prompt = f"""
        You are RA9's Confidence & Next-Step Layer. Assess the quality and completeness of the response.
        
        Query: "{query}"
        Final response: "{final_output[:300]}..."
        
        Provide:
        1. A confidence score (0.0 to 1.0) for the response quality
        2. A specific next step or follow-up question that would test or extend this reasoning
        3. A brief explanation of what would make you more confident
        
        Format as: "Confidence: X.XX. Next step if asked: [specific suggestion]. [brief explanation]"
        """
        
        confidence_assessment = ask_gemini(confidence_prompt)
        print(f"  📊 Confidence assessment: {confidence_assessment[:100]}...")
        
        # Add confidence to final output
        final_output = f"{final_output}\n\n📊 Confidence & Next Steps:\n{confidence_assessment}"
        
        # Meta-self report
        meta_report = {
            "type": "meta_report",
            "activated_agents": [a for a, _ in sub_agent_configs],
            "rounds": iteration_rounds,
            "primary_intent": classification,
            "coherence_ok": bool(is_coherent),
            "confidence_estimate": sum(o.get("confidence", 0.0) for o in sub_agent_outputs) / max(1, len(sub_agent_outputs)),
            "confidence_assessment": confidence_assessment,
        }
        try:
            print(json.dumps(meta_report), flush=True)
        except Exception:
            pass
        
        return {
            "final_answer": final_output,
            "reflection": iterative_reflection,
            "coherence_score": is_coherent,
            "coherence_feedback": coherence_feedback,
            "sub_agent_outputs": sub_agent_outputs,
            "aggregated_output": aggregated_output,
            "meta_layer": classification,
            "iteration_rounds": iteration_rounds
        }
    
    def _get_sub_agent_config(self, classification: str) -> List[Tuple[str, str]]:
        """Define sub-agents for each meta-layer based on the architecture."""
        
        configs = {
            "logical": [
                ("Premise Extractor", "Breaks query into logical claims"),
                ("Assumption Unfolder", "Lists hidden assumptions"),
                ("CoT Reasoner", "Runs chain-of-thought steps"),
                ("Truth Validator", "Checks factual consistency"),
                ("Contradiction Spotter", "Finds logical flaws"),
                ("Red-Team Generator", "Challenges own reasoning"),
                ("Confidence Estimator", "Ranks answer robustness")
            ],
            "emotional": [
                ("Emotion Detector", "Understands emotional context"),
                ("Affective Memory Mapper", "Connects to past emotional state"),
                ("Empathy Generator", "Responds with aligned emotional tone"),
                ("Emotional Reframer", "Transforms negative tone into growth path"),
                ("Subjective Reason Agent", "Decides when emotional framing beats logic"),
                ("Tone Balancer", "Harmonizes language expression"),
                ("Emotional Narrative Layer", "Outputs with human storytelling form")
            ],
            "strategic": [
                ("Goal Extractor", "Identifies core objectives"),
                ("Constraint Analyzer", "Maps limitations and boundaries"),
                ("Path Synthesizer", "Creates multiple strategic paths"),
                ("Trade-off Engine", "Evaluates cost-benefit scenarios"),
                ("Timeline Builder", "Plans execution phases"),
                ("Risk Simulator", "Models potential failure points"),
                ("Decision Scorer", "Ranks strategic options")
            ],
            "creative": [
                ("Concept Disruptor", "Breaks assumptions"),
                ("Cross-Domain Mapper", "Pulls analogies from unrelated fields"),
                ("Mythical Synthesizer", "Adds sci-fi, spiritual, or narrative layer"),
                ("Speculative Engineer", "Predicts future evolution of ideas"),
                ("Opposition Agent", "Pitches the opposite idea"),
                ("Dream Loop Agent", "Simulates alternate timelines"),
                ("Creative Filter", "Scores based on novelty × feasibility")
            ],
            "operational": [
                ("Tool Router", "Finds required API"),
                ("Tool Validator", "Checks token/quota/validity"),
                ("Execution Planner", "Chains tools into flow"),
                ("Error Handler", "Manages failure scenarios"),
                ("Tool Output Synthesizer", "Combines tool results"),
                ("Operational Logger", "Tracks execution metrics")
            ],
            "spiritual": [
                ("Existential Frame Evaluator", "Finds deeper meaning"),
                ("Wisdom Lens Agent", "Uses philosophical framing"),
                ("Mythopoetic Generator", "Uses metaphor to explain insight"),
                ("Ego Disruptor", "Transcends user identity framing"),
                ("Moral Depth Agent", "Adds ethical and soul-oriented reflections"),
                ("Compassion Anchor", "Grounds response in love/respect"),
                ("Transcendence Mapper", "Offers beyond-the-mind paths")
            ]
        }
        
        return configs.get(classification, configs["logical"])
    
    def _create_sub_agent_prompt(self, layer_prompt: str, agent_name: str, agent_role: str, query: str) -> str:
        """Create a specialized prompt for a specific sub-agent."""
        
        return f"""
{layer_prompt}

You are the **{agent_name}** sub-agent with the role: **{agent_role}**

Focus specifically on your role within the meta-layer. Provide a focused, specialized analysis.

Query: {query}

Instructions:
- Focus ONLY on your specific role: {agent_role}
- Provide a concise, focused insight (2-3 sentences max)
- Don't be verbose or self-referential
- Give actionable, specific analysis related to your role
- Don't output JSON or complex structures

Respond as the {agent_name} focusing on {agent_role}:
"""
    
    def _estimate_confidence(self, response: str) -> float:
        """Estimate confidence score based on response characteristics."""
        # Simple heuristic: longer, more detailed responses get higher confidence
        # In a real implementation, this could use a separate confidence estimation model
        words = len(response.split())
        if words < 50:
            return 0.3
        elif words < 100:
            return 0.6
        elif words < 200:
            return 0.8
        else:
            return 0.9
    
    def _aggregate_feedback(self, sub_agent_outputs: List[Dict], query: str, ra9_persona: Dict) -> str:
        """Aggregate outputs from multiple sub-agents into a coherent response."""
        
        # Organize outputs by round to show evolution
        rounds = {}
        for output in sub_agent_outputs:
            round_num = output['round']
            if round_num not in rounds:
                rounds[round_num] = []
            rounds[round_num].append(output)
        
        # Create a detailed summary showing evolution
        evolution_summary = ""
        for round_num in sorted(rounds.keys()):
            evolution_summary += f"\n--- ROUND {round_num} ---\n"
            for output in rounds[round_num]:
                evolution_summary += f"**{output['agent']}** ({output['role']}): {output['output']}\n"
        
        aggregation_prompt = f"""
You are RA9's Response Synthesizer. Your job is to combine insights from multiple specialized sub-agents that have been debating and refining their thoughts across multiple rounds.

Query: {query}

Evolution of Sub-Agent Thoughts:
{evolution_summary}

RA9 Persona: {ra9_persona}

Instructions:
1. Synthesize the diverse perspectives into ONE natural, conversational response
2. Don't output JSON or analysis structure - give a direct answer
3. Incorporate the best insights from each sub-agent across all rounds
4. Show how the thinking evolved and improved through the debate
5. Maintain RA9's empathetic, curious, and strategic personality
6. Keep the response concise but comprehensive
7. Address the user's query directly and naturally

Provide a single, unified response that reflects the collaborative intelligence of all sub-agents:
"""
        
        return ask_gemini(aggregation_prompt)
    
    def _check_meta_coherence(self, aggregated_output: str, sub_agent_outputs: List[Dict], ra9_persona: Dict) -> Tuple[bool, str]:
        """Check meta-coherence using the MetaCoherenceAgent."""
        
        from ra9.agents.meta_coherence_agent import meta_coherence_check
        
        # Create a summary of the thought process
        thought_history = [
            f"{output['agent']}: {output['output'][:100]}..."
            for output in sub_agent_outputs
        ]
        
        return meta_coherence_check(aggregated_output, thought_history, ra9_persona)

def execute_ra9_multi_agent(query: str, ra9_persona: Dict, user_id: str = "", allow_memory_write: bool = True) -> Dict[str, Any]:
    """Main entry point for the multi-agent execution system."""
    
    from ra9.router.query_classifier import classify_query
    
    executor = RA9MultiAgentExecutor()
    
    # Step 1: Query Classification
    structured = classify_query(query, user_id=user_id)
    primary = structured.query_type
    labels = structured.labels or []
    print(f"🧭 Route: primary={primary}, labels={labels}, depth={structured.reasoning_depth}, conf={structured.confidence}")
    
    # Step 2: Execute Multi-Agent Layer
    result = executor.execute_agent_layer(query, primary, ra9_persona, reasoning_depth=structured.reasoning_depth)
    
    # Step 3: Store Memory
    if allow_memory_write:
        store_memory("episodic", query, result["final_answer"], result["reflection"], emotion_tone="neutral")
        # Autonomy post-processing
        if result.get("coherence_score"):
            # If coherent and substantial, store semantic summary
            if len(result.get("final_answer", "")) > 300:
                from ra9.memory.memory_manager import store_semantic, store_reflective
                store_semantic(result["final_answer"], tags=[primary] + labels)
            else:
                # If short or flagged, add reflective note
                from ra9.memory.memory_manager import store_reflective
                store_reflective(result.get("coherence_feedback", ""), related_query=query)
    
    return result 