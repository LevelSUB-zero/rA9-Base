from ra9.tools.tool_api import ask_gemini
import json
import re

def analyze_query_complexity(query):
    """Analyze if a query requires the full multi-agent system or can be answered directly."""
    
    # Simple patterns that don't need multi-agent processing
    simple_patterns = [
        "what's my name",
        "what is my name", 
        "what time",
        "what's the time",
        "what is the time",
        "what day",
        "what's the date",
        "what is the date",
        "how are you",
        "hello",
        "hi",
        "bye",
        "goodbye",
        "thanks",
        "thank you",
        "what's 2+2",
        "what is 2+2",
        "calculate",
        "math",
        "simple question",
        "basic question"
    ]
    
    # Check for simple patterns
    query_lower = query.lower().strip() # Strip whitespace
    for pattern in simple_patterns:
        if query_lower == pattern or query_lower.startswith(f"{pattern} ") or query_lower.endswith(f" {pattern}"):
            return "simple", f"Query matches simple pattern: {pattern}"
    
    # Use AI to analyze complexity for ambiguous cases
    complexity_prompt = f"""
Analyze this query and determine if it requires deep, multi-agent cognitive processing or can be answered with a simple, direct response.

Query: "{query}"

Consider:
- Does it require emotional intelligence, strategic thinking, or creative problem-solving?
- Is it a factual question that can be answered directly?
- Does it involve personal reflection, philosophical depth, or complex reasoning?
- Is it a simple greeting, basic math, or straightforward information request?

Respond with either:
"SIMPLE: [brief reason]" - for questions that don't need multi-agent processing
"COMPLEX: [brief reason]" - for questions that benefit from multi-agent debate

Your analysis:
"""
    
    try:
        analysis = ask_gemini(complexity_prompt)
        if "SIMPLE:" in analysis:
            return "simple", analysis
        elif "COMPLEX:" in analysis:
            return "complex", analysis
        else:
            # Default to complex if analysis is unclear
            return "complex", "Analysis unclear, defaulting to complex processing"
    except:
        # If AI analysis fails, use pattern matching as fallback
        return "complex", "AI analysis failed, defaulting to complex processing"

def should_use_multi_agent(query):
    """Determine if query should use the full multi-agent system."""
    complexity, reason = analyze_query_complexity(query)
    return complexity == "complex", reason 


def select_agents_for_query(query):
    """Use the LLM to propose an optimal subset of agents for deep/critical analysis.

    Returns a list of agent keys from the allowed set:
    ["logical", "emotional", "strategic", "creative", "operational", "spiritual",
     "knowledge", "search", "code", "graphical", "ethical", "brain_tool"].
    """
    allowed_agents = [
        "logical", "emotional", "strategic", "creative", "operational", "spiritual",
        "knowledge", "search", "code", "graphical", "ethical", "brain_tool"
    ]

    prompt = f"""
    You are RA9's agent selector. Given the user query, choose ONLY the most relevant sub-agents
    from this fixed set (return 3-8 agents):
    {allowed_agents}

    Query: {query}

    Rules:
    - Pick agents strictly from the allowed list.
    - Prefer minimal yet sufficient sets (3-6) for focus and speed.
    - Output STRICT JSON only:
      {{
        "agents": ["agent1", "agent2", ...],
        "reason": "very brief justification"
      }}
    """

    try:
        raw = ask_gemini(prompt)
        # Direct parse
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if not m:
                raise ValueError("No JSON in response")
            data = json.loads(m.group(0))

        agents = [a for a in data.get("agents", []) if a in allowed_agents]
        # Clamp size
        if len(agents) < 3:
            agents = _fallback_agent_heuristics(query)
        return agents[:8]
    except Exception:
        return _fallback_agent_heuristics(query)


def _fallback_agent_heuristics(query):
    q = query.lower()
    agents = set(["logical"])  # always include logical
    if any(k in q for k in ["plan", "strategy", "roadmap", "optimize", "risk"]):
        agents.add("strategic")
    if any(k in q for k in ["feel", "emotion", "empathy", "human", "motivation"]):
        agents.add("emotional")
    if any(k in q for k in ["novel", "creative", "ideas", "brainstorm"]):
        agents.add("creative")
    if any(k in q for k in ["implement", "build", "deploy", "run", "practical"]):
        agents.add("operational")
    if any(k in q for k in ["ethic", "fair", "moral", "harm"]):
        agents.add("ethical")
    if any(k in q for k in ["search", "current", "latest", "news", "web"]):
        agents.add("search")
    if any(k in q for k in ["code", "algorithm", "complexity", "compute"]):
        agents.add("code")
    if any(k in q for k in ["interpret", "explain", "understand", "knowledge", "summarize"]):
        agents.add("knowledge")
    if any(k in q for k in ["diagram", "graph", "visual"]):
        agents.add("graphical")
    if any(k in q for k in ["philosophy", "meaning", "purpose", "consciousness", "spiritual"]):
        agents.add("spiritual")
    return list(agents)[:6]