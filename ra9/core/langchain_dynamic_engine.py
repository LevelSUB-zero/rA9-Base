import time
from typing import Dict, Any, List
from core.dynamic_reflection_engine import DynamicReflectionEngine
from core.langchain_integration import create_langchain_integration
from core.enhanced_cli_ui import create_enhanced_cli
from ra9.memory.memory_manager import store_memory

class RA9LangChainDynamicEngine:
    """Ultra-powerful engine combining our dynamic reflection with LangChain capabilities."""
    
    def __init__(self):
        self.dynamic_engine = DynamicReflectionEngine()
        self.langchain_integration = create_langchain_integration()
        self.cli = create_enhanced_cli()
        
    def process_query(self, query: str, ra9_persona: Dict) -> Dict[str, Any]:
        """Process query using the most appropriate method based on complexity."""
        
        start_time = time.time()
        
        # Step 1: Analyze query complexity
        complexity_analysis = self._analyze_complexity(query)
        complexity_level = complexity_analysis.get("complexity", 7)
        
        self.cli.show_processing_start(query, f"Level {complexity_level}/10")
        
        # Step 2: Choose processing method
        if complexity_level <= 3:
            # Simple queries - use LangChain agent executor
            return self._process_simple_query(query, start_time)
        elif complexity_level <= 7:
            # Moderate complexity - use our dynamic engine
            return self._process_moderate_query(query, ra9_persona, start_time)
        else:
            # Ultra-complex - use LangChain workflow + our dynamic engine
            return self._process_ultra_complex_query(query, ra9_persona, start_time)
    
    def _analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity using LangChain."""
        
        analysis_prompt = f"""
        Analyze this query and determine its complexity level:
        
        Query: "{query}"
        
        Consider:
        - Does it require factual information?
        - Does it need emotional intelligence?
        - Does it require strategic thinking?
        - Does it involve philosophical depth?
        - Does it need tool usage (search, calculation, etc.)?
        
        Respond in JSON format:
        {{
            "complexity": <1-10>,
            "processing_method": "simple|moderate|ultra_complex",
            "tools_needed": ["tool1", "tool2"],
            "reasoning_type": "factual|emotional|strategic|philosophical"
        }}
        """
        
        try:
            result = self.langchain_integration.llm.invoke([analysis_prompt])
            import json
            return json.loads(result.content)
        except:
            return {
                "complexity": 7,
                "processing_method": "moderate",
                "tools_needed": [],
                "reasoning_type": "strategic"
            }
    
    def _process_simple_query(self, query: str, start_time: float) -> Dict[str, Any]:
        """Process simple queries using LangChain agent executor."""
        
        self.cli.show_phase_progress("SIMPLE PROCESSING", "Using LangChain agent executor with tools")
        
        try:
            # Create agent executor
            agent_executor = self.langchain_integration.create_agent_executor()
            
            # Execute query
            result = agent_executor.invoke({"input": query})
            
            processing_time = time.time() - start_time
            
            return {
                "final_answer": result["output"],
                "processing_type": "simple",
                "processing_time": processing_time,
                "tools_used": result.get("intermediate_steps", []),
                "iterations": 1
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "final_answer": f"Error processing query: {str(e)}",
                "processing_type": "simple_error",
                "processing_time": processing_time,
                "tools_used": [],
                "iterations": 1
            }
    
    def _process_moderate_query(self, query: str, ra9_persona: Dict, start_time: float) -> Dict[str, Any]:
        """Process moderate complexity queries using our dynamic engine."""
        
        self.cli.show_phase_progress("MODERATE PROCESSING", "Using dynamic reflection engine")
        
        try:
            # Use our existing dynamic engine
            result = self.dynamic_engine.orchestrate_deep_processing(query, ra9_persona)
            
            processing_time = time.time() - start_time
            
            return {
                "final_answer": result["final_answer"],
                "processing_type": "moderate",
                "processing_time": processing_time,
                "iterations": result["iterations"],
                "agents_used": result["agents_used"],
                "debate_history": result["debate_history"]
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "final_answer": f"Error processing query: {str(e)}",
                "processing_type": "moderate_error",
                "processing_time": processing_time,
                "iterations": 0,
                "agents_used": [],
                "debate_history": []
            }
    
    def _process_ultra_complex_query(self, query: str, ra9_persona: Dict, start_time: float) -> Dict[str, Any]:
        """Process ultra-complex queries using LangChain workflow + dynamic engine."""
        
        self.cli.show_phase_progress("ULTRA-COMPLEX PROCESSING", "Using LangChain workflow + dynamic reflection")
        
        try:
            # Step 1: Use LangChain workflow for initial analysis and tool usage
            self.cli.show_phase_progress("LANGCHAIN WORKFLOW", "Initial analysis and tool integration")
            langchain_result = self.langchain_integration.execute_langchain_workflow(query)
            
            # Step 2: Use our dynamic engine for deep reflection
            self.cli.show_phase_progress("DYNAMIC REFLECTION", "Deep multi-agent debate and synthesis")
            
            # Enhance the query with LangChain results
            enhanced_query = f"""
            Original Query: {query}
            
            LangChain Analysis Results:
            - Tools Used: {langchain_result.get('tools_used', [])}
            - Initial Analysis: {langchain_result.get('final_answer', '')}
            
            Please provide a deeper, more philosophical and comprehensive analysis.
            """
            
            dynamic_result = self.dynamic_engine.orchestrate_deep_processing(enhanced_query, ra9_persona)
            
            # Step 3: Synthesize both results
            synthesis_prompt = f"""
            Synthesize these two analyses into the ultimate response:
            
            Original Query: {query}
            
            LangChain Analysis: {langchain_result['final_answer']}
            Dynamic Reflection Analysis: {dynamic_result['final_answer']}
            
            Create a comprehensive response that combines:
            1. Factual accuracy and tool usage from LangChain
            2. Deep philosophical insight and emotional intelligence from dynamic reflection
            3. Practical applicability and strategic thinking
            
            Final Response:
            """
            
            final_synthesis = self.langchain_integration.llm.invoke([synthesis_prompt])
            
            processing_time = time.time() - start_time
            
            return {
                "final_answer": final_synthesis.content,
                "processing_type": "ultra_complex",
                "processing_time": processing_time,
                "iterations": dynamic_result["iterations"] + langchain_result["iterations"],
                "agents_used": dynamic_result["agents_used"],
                "langchain_tools": langchain_result.get("tools_used", []),
                "debate_history": dynamic_result["debate_history"]
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "final_answer": f"Error processing ultra-complex query: {str(e)}",
                "processing_type": "ultra_complex_error",
                "processing_time": processing_time,
                "iterations": 0,
                "agents_used": [],
                "debate_history": []
            }
    
    def store_experience(self, query: str, result: Dict[str, Any]):
        """Store the processing experience in memory."""
        
        experience_data = {
            "query": query,
            "processing_type": result["processing_type"],
            "processing_time": result["processing_time"],
            "iterations": result.get("iterations", 0),
            "agents_used": result.get("agents_used", []),
            "tools_used": result.get("langchain_tools", [])
        }
        
        # Store in both traditional and vector memory
        store_memory(
            result["processing_type"], 
            query, 
            result["final_answer"], 
            f"Processing experience: {experience_data}"
        )
        
        # Store in LangChain vector memory
        self.langchain_integration.store_memory(
            str(experience_data),
            {"category": "processing_experience", "type": result["processing_type"]}
        )

def create_langchain_dynamic_engine():
    """Create and return the LangChain-enhanced dynamic engine."""
    return RA9LangChainDynamicEngine() 