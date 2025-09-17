from ra9.tools.tool_api import ask_gemini, load_prompt_from_json

# Load the prompt for the Reflective Agent
REFLECTIVE_AGENT_PROMPT = load_prompt_from_json("ra9/Prompts/ra9-v0.01 alpha/RA9ReflectiveLayerPrompt.json")

def reflect_response(context, answer, persona=None):
    persona_values = ""
    if persona and 'core_values' in persona:
        persona_values = "\nRA9's Core Values: " + ", ".join(persona['core_values'])

    prompt = f"""
{REFLECTIVE_AGENT_PROMPT}
    Consider RA9's persona during evaluation.{persona_values}

    Context: {context}
    Answer: {answer}
    
    Reflect on how well the answer was constructed. Suggest any adjustments if needed. Also, briefly comment on the response's alignment with RA9's core values if applicable.
    """
    
    return ask_gemini(prompt)