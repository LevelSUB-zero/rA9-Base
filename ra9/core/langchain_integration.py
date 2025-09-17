import os
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class RA9LangChainIntegration:
    """Advanced LangChain integration for RA9's cognitive system."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            max_tokens=4000
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input"
        )
        
        self.vector_memory = None
        self.tools = []
        self.agent_executor = None
        self.workflow_graph = None
        
        self._initialize_tools()
        self._initialize_vector_memory()
        self._initialize_workflow()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def _call_llm(self, prompt_template, **kwargs):
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.invoke(kwargs)

    def _initialize_tools(self):
        """Initialize LangChain tools for RA9."""
        
        # Search tools
        search_tool = DuckDuckGoSearchRun()
        wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        
        # Custom tools for RA9
        def calculate_tool(expression: str) -> str:
            """Calculate mathematical expressions."""
            try:
                return str(eval(expression))
            except:
                return "Error: Invalid mathematical expression"
        
        def memory_store_tool(content: str, category: str = "general") -> str:
            """Store information in RA9's memory."""
            try:
                if self.vector_memory:
                    self.vector_memory.add_texts([content], metadatas=[{"category": category}])
                return f"Stored in memory under category: {category}"
            except:
                return "Error storing in memory"
        
        def memory_retrieve_tool(query: str, category: str = None) -> str:
            """Retrieve information from RA9's memory."""
            try:
                if self.vector_memory:
                    if category:
                        results = self.vector_memory.similarity_search(query, k=3, filter={"category": category})
                    else:
                        results = self.vector_memory.similarity_search(query, k=3)
                    return "\n".join([doc.page_content for doc in results])
                return "No memory available"
            except:
                return "Error retrieving from memory"
        
        # Create tool objects
        self.tools = [
            Tool(
                name="web_search",
                description="Search the web for current information",
                func=search_tool.run
            ),
            Tool(
                name="wikipedia",
                description="Search Wikipedia for detailed information",
                func=wikipedia_tool.run
            ),
            Tool(
                name="calculator",
                description="Calculate mathematical expressions",
                func=calculate_tool
            ),
            Tool(
                name="memory_store",
                description="Store information in RA9's memory",
                func=memory_store_tool
            ),
            Tool(
                name="memory_retrieve",
                description="Retrieve information from RA9's memory",
                func=memory_retrieve_tool
            )
        ]
    
    def _initialize_vector_memory(self):
        """Initialize vector memory for RA9."""
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            self.vector_memory = Chroma(
                collection_name="ra9_memory",
                embedding_function=embeddings,
                persist_directory="./memory/vector_store"
            )
        except Exception as e:
            print(f"Warning: Vector memory initialization failed: {e}")
            self.vector_memory = None
    
    def _initialize_workflow(self):
        """Initialize LangGraph workflow for RA9."""
        
        # Define the state schema
        class RA9State:
            def __init__(self):
                self.query = ""
                self.agents = []
                self.debate_results = {}
                self.final_answer = ""
                self.iteration = 0
                self.quality_score = 0.0
                self.tools_used = []
                self.feedback = "" # New field for feedback
        
        # Create workflow graph
        workflow = StateGraph(RA9State)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query_node)
        workflow.add_node("select_agents", self._select_agents_node)
        workflow.add_node("agent_debate", self._agent_debate_node)
        workflow.add_node("assess_quality", self._assess_quality_node)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Add edges
        workflow.set_entry_point("analyze_query") # Set the entry point for the workflow
        workflow.add_edge("analyze_query", "select_agents")
        workflow.add_edge("select_agents", "agent_debate")
        workflow.add_edge("agent_debate", "assess_quality")
        workflow.add_conditional_edges(
            "assess_quality",
            self._should_continue,
            {
                "continue": "agent_debate",
                "synthesize": "synthesize",
                END: END
            }
        )
        workflow.add_edge("synthesize", END)
        
        self.workflow_graph = workflow.compile()
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def _analyze_query_node(self, state):
        """Analyze the query complexity and requirements."""
        analysis_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Analyze this query and determine its complexity and requirements:
            
            Query: {query}
            
            Respond in JSON format:
            {{
                "complexity": <1-10>,
                "required_agents": ["agent1", "agent2"],
                "tools_needed": ["tool1", "tool2"],
                "reasoning_depth": "<description>"
            }}
            """
        )
        
        result = self._call_llm(analysis_prompt, query=state.query)
        
        try:
            analysis = json.loads(result.content)
            state.analysis = analysis
        except:
            state.analysis = {
                "complexity": 7,
                "required_agents": ["logical", "emotional"],
                "tools_needed": [],
                "reasoning_depth": "Moderate complexity"
            }
        
        return state
    
    def _select_agents_node(self, state):
        """Select optimal agents based on analysis."""
        state.agents = state.analysis.get("required_agents", ["logical", "emotional"])
        return state
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def _agent_debate_node(self, state):
        """Execute agent debate round."""
        state.iteration += 1
        
        for agent in state.agents:
            agent_prompt = PromptTemplate(
                input_variables=["query", "agent", "previous_results", "tools_available", "previous_feedback"],
                template="""
                You are the {agent} agent in RA9's cognitive system.
                
                Query: {query}
                Previous Results: {previous_results}
                Available Tools: {tools_available}
                Previous Feedback for Improvement: {previous_feedback}
                
                Provide your analysis and perspective, considering the feedback for improvement:
                """
            )
            
            result = self._call_llm(
                agent_prompt,
                query=state.query,
                agent=agent,
                previous_results=str(state.debate_results),
                tools_available=[tool.name for tool in self.tools],
                previous_feedback=state.feedback
            )
            
            state.debate_results[agent] = result.content # Store content of the result
        
        return state
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def _assess_quality_node(self, state):
        """Assess the quality of current results."""
        assessment_prompt = PromptTemplate(
            input_variables=["query", "results", "iteration"],
            template="""
            Assess the quality of these debate results for the given query. Provide **specific, actionable feedback** on what needs to be improved to achieve a perfect 10/10 score. Suggest concrete approaches or areas of focus for the next iteration.

            Query: {query}
            Results: {results}
            Iteration: {iteration}

            Rate from 1-10 and provide detailed, actionable feedback. Ensure your response is in strict JSON format:
            {
                "score": <number, 1-10>,
                "feedback": "<detailed, actionable feedback for improvement>",
                "should_continue": <true/false, based on whether further iterations are needed to reach 10/10>
            }
            """
        )
        
        result = self._call_llm(assessment_prompt, query=state.query, results=str(state.debate_results), iteration=state.iteration)
        
        print(f"DEBUG: Raw LLM response for quality assessment: {result.content}", flush=True)

        try:
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                json_string = json_match.group(0)
                assessment = json.loads(json_string)
                state.quality_score = assessment.get("score", 5.0) # Default to 5.0 for robustness
                state.should_continue = assessment.get("should_continue", True)
                state.feedback = assessment.get("feedback", "No specific feedback provided.")
            else:
                raise ValueError("No JSON object found in LLM response.")
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed for quality assessment: {e}. Raw response: {result.content}")
            state.quality_score = 3.0 # Significantly lower score for unparseable JSON
            state.should_continue = True # Force continuation to attempt self-correction
            state.feedback = f"Quality assessment failed: Invalid JSON response. Error: {e}. Raw: {result.content}"
        except Exception as e:
            print(f"Error in quality assessment parsing: {e}. Raw response: {result.content}")
            state.quality_score = 3.0 # Significantly lower score for other errors
            state.should_continue = True # Force continuation
            state.feedback = f"Quality assessment failed due to unexpected error: {e}. Raw: {result.content}"
        
        return state
    
    def _should_continue(self, state):
        """Determine if the workflow should continue based on quality score and explicit feedback."""
        print(f"Current Quality Score: {state.quality_score}, Should Continue Flag: {state.should_continue}, Iteration: {state.iteration}", flush=True)
        if state.quality_score >= 9.5 and not state.should_continue:
            print("Synthesizing final answer: High quality and assessment says no more iterations.", flush=True)
            return "synthesize"
        elif state.iteration >= 10:
            print("Ending workflow: Max iterations reached.", flush=True)
            return END
        elif state.should_continue and state.quality_score < 9.5:
            print("Continuing debate: Assessment suggests more iterations needed.", flush=True)
            return "continue"
        else:
            print("Synthesizing final answer: Defaulting to synthesize as no clear continuation signal.", flush=True)
            return "synthesize" # Default to synthesize if no clear path
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def _synthesize_node(self, state):
        """Synthesize final answer from all debate results."""
        synthesis_prompt = PromptTemplate(
            input_variables=["query", "results", "quality_score"],
            template="""
            Synthesize the final answer from all agent debate results:
            
            Query: {query}
            Debate Results: {results}
            Quality Score: {quality_score}/10
            
            Create a comprehensive, well-structured response:
            """
        )
        
        state.final_answer = self._call_llm(
            synthesis_prompt,
            query=state.query,
            results=str(state.debate_results),
            quality_score=state.quality_score
        ).content
        
        return state
    
    def execute_langchain_workflow(self, query: str) -> Dict[str, Any]:
        """Execute the complete LangChain workflow."""
        
        # Initialize state
        state = type('State', (), {
            'query': query,
            'agents': [],
            'debate_results': {},
            'final_answer': "",
            'iteration': 0,
            'quality_score': 0.0,
            'tools_used': [],
            'feedback': "" # Initialize new field
        })()
        
        # Execute workflow
        final_state = self.workflow_graph.invoke(state)
        
        return {
            "final_answer": final_state.final_answer,
            "iterations": final_state.iteration,
            "quality_score": final_state.quality_score,
            "agents_used": final_state.agents,
            "debate_results": final_state.debate_results
        }
    
    def create_agent_executor(self, tools: List[Tool] = None) -> AgentExecutor:
        """Create a LangChain agent executor with tools."""
        
        if tools is None:
            tools = self.tools
        
        # Create agent prompt
        agent_prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad"],
            template="""
            You are RA9, an advanced AI with multiple cognitive agents.
            
            Available tools: {tools}
            
            Use the following format:
            
            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question
            
            Question: {input}
            {agent_scratchpad}
            """
        )
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=agent_prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10
        )
        
        return self.agent_executor
    
    def store_memory(self, content: str, metadata: Dict = None):
        """Store content in vector memory."""
        if self.vector_memory:
            if metadata is None:
                metadata = {"category": "general"}
            self.vector_memory.add_texts([content], metadatas=[metadata])
    
    def retrieve_memory(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant content from memory."""
        if self.vector_memory:
            results = self.vector_memory.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        return []

def create_langchain_integration():
    """Create and return LangChain integration instance."""
    return RA9LangChainIntegration() 