from ra9.tools.tool_api import ask_gemini, load_prompt_from_json
from .base_agent import BaseAgent, AgentResult
from typing import Dict, Any

# Load the prompt for the Feedback Agent
FEEDBACK_AGENT_PROMPT = load_prompt_from_json("ra9/Prompts/ra9-v0.01 alpha/RA9FeedbackAggregationLayerPrompt.json")


class FeedbackAgent(BaseAgent):
    """Feedback agent for refining responses based on feedback."""
    
    def __init__(self):
        super().__init__(
            name="FeedbackAgent",
            description="Refines responses based on user feedback"
        )
    
    def process_query(self, query: str, context: Dict[str, Any]) -> AgentResult:
        """Process feedback and refine response."""
        try:
            original_query = context.get("original_query", "")
            current_response = context.get("current_response", "")
            feedback_context = context.get("feedback_context", "")
            ra9_persona = context.get("ra9_persona", {})
            
            refined_response = self._refine_response(
                original_query, current_response, feedback_context, ra9_persona
            )
            
            return AgentResult(
                answer=refined_response,
                quality_score=8.5,
                confidence=0.9,
                reasoning="Response refined based on feedback"
            )
            
        except Exception as e:
            return AgentResult(
                answer=f"Feedback processing failed: {str(e)}",
                quality_score=2.0,
                confidence=0.1,
                reasoning="Error in feedback processing"
            )
    
    def _refine_response(self, original_query: str, current_response: str, 
                        feedback_context: str, ra9_persona: Dict[str, Any]) -> str:
        """Refine response based on feedback."""
        prompt = f"""
{FEEDBACK_AGENT_PROMPT}

Review the following original query, the current response, and provided feedback. Your task is to refine the current response based on the feedback, while keeping RA9's persona in mind.

Original Query: {original_query}
Current Response: {current_response}
Feedback Context: {feedback_context}
RA9 Persona: {ra9_persona}

Provide a refined response. Be concise and address the feedback directly.
"""
        return ask_gemini(prompt)


def aggregate_and_refine_feedback(original_query, current_response, feedback_context, ra9_persona):
    prompt = f"""
{FEEDBACK_AGENT_PROMPT}

Review the following original query, the current response, and provided feedback. Your task is to refine the current response based on the feedback, while keeping RA9's persona in mind.

Original Query: {original_query}
Current Response: {current_response}
Feedback Context: {feedback_context}
RA9 Persona: {ra9_persona}

Provide a refined response. Be concise and address the feedback directly.
"""
    return ask_gemini(prompt)