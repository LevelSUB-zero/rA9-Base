from ra9.memory.memory_manager import get_user_name, check_user_context, store_user_info
from datetime import datetime
import time
from ra9.tools.tool_api import ask_gemini

def handle_simple_query(query):
    """Handle simple queries with AI-generated responses (faster than multi-agent)."""
    
    query_lower = query.lower()
    
    # Check for user context updates first
    context_type, context_value = check_user_context(query)
    if context_type == "name":
        store_user_info("name", context_value)
        user_name = context_value
        return f"Got it! I'll call you {user_name} from now on. Nice to meet you!"
    
    # Get user name for personalized responses
    user_name = get_user_name()
    
    # Handle different types of simple queries with AI generation
    if "what's my name" in query_lower or "what is my name" in query_lower:
        if user_name != "User":
            return f"Your name is {user_name}!"
        else:
            return "I don't know your name yet. You can tell me by saying something like 'call me [your name]' or 'my name is [your name]'."
    
    elif "what time" in query_lower:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    elif "what day" in query_lower or "what's the date" in query_lower:
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}."
    
    elif any(math_word in query_lower for math_word in ["calculate", "math", "+", "-", "*", "/", "×", "÷", "plus", "minus", "times", "divided"]):
        # Use AI for math calculations
        math_prompt = f"""
You are a helpful math assistant. Solve this math problem and provide a clear, direct answer.

Problem: {query}

Instructions:
- Solve the mathematical expression
- Provide the answer in a clear format
- If it's a simple calculation, show the steps briefly
- Be concise and accurate

Answer:
"""
        try:
            return ask_gemini(math_prompt)
        except:
            return f"Sorry {user_name}, I couldn't process that math problem. Could you rephrase it?"
    
    elif "hello" in query_lower or "hi" in query_lower:
        greeting_prompt = f"""
Generate a friendly, personalized greeting for {user_name}.

Keep it warm, natural, and under 2 sentences. Make it feel personal.
"""
        try:
            return ask_gemini(greeting_prompt)
        except:
            return f"Hello {user_name}! How can I help you today?"
    
    elif "how are you" in query_lower:
        response_prompt = f"""
Generate a friendly response to "how are you" for {user_name}.

Keep it warm, natural, and under 2 sentences. Show genuine care.
"""
        try:
            return ask_gemini(response_prompt)
        except:
            return f"I'm doing well, {user_name}! Thank you for asking. How are you?"
    
    elif "bye" in query_lower or "goodbye" in query_lower:
        goodbye_prompt = f"""
Generate a warm goodbye message for {user_name}.

Keep it friendly and under 2 sentences. Make it feel personal.
"""
        try:
            return ask_gemini(goodbye_prompt)
        except:
            return f"Goodbye {user_name}! It was nice talking with you."
    
    elif "thanks" in query_lower or "thank you" in query_lower:
        thanks_prompt = f"""
Generate a warm response to "thank you" for {user_name}.

Keep it friendly and under 2 sentences. Show genuine appreciation.
"""
        try:
            return ask_gemini(thanks_prompt)
        except:
            return f"You're welcome, {user_name}! I'm happy to help."
    
    else:
        # For other simple queries, use AI to generate a helpful response
        simple_prompt = f"""
You are RA9, a helpful AI assistant. {user_name} has asked: "{query}"

This appears to be a simple question that doesn't require deep multi-agent processing. Provide a helpful, direct answer.

Guidelines:
- Be concise and clear
- Show personality and warmth
- Address {user_name} by name
- Keep it under 3 sentences
- Be genuinely helpful

Response:
"""
        try:
            return ask_gemini(simple_prompt)
        except:
            return f"I understand you're asking about '{query}', {user_name}. This seems like a simple question, but I might need more context to give you the best answer. Would you like me to think about this more deeply?" 