from ra9.tools.tool_api import ask_gemini, load_prompt_from_json

# Load the prompt for the Feedback Agent
FEEDBACK_AGENT_PROMPT = load_prompt_from_json("ra9/Prompts/ra9-v0.01 alpha/RA9FeedbackAggregationLayerPrompt.json")

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