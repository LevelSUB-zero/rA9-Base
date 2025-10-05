import requests, os
from dotenv import load_dotenv
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, Any, Optional

load_dotenv()


class ToolAPI:
    """API wrapper for various tools and services."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    def ask_gemini(self, prompt: str) -> str:
        """Call Gemini API with retry logic."""
        return ask_gemini(prompt)
    
    def load_prompt(self, file_path: str) -> str:
        """Load prompt from JSON file."""
        return load_prompt_from_json(file_path)
    
    def is_configured(self) -> bool:
        """Check if API keys are configured."""
        return bool(self.gemini_api_key or self.openai_api_key)

def load_prompt_from_json(file_path):
    try:
        with open(file_path, 'r') as f:
            prompt_data = json.load(f)
            
            # For agents with detailed meta-layer prompts
            if "purpose" in prompt_data and "responseGuidelines" in prompt_data:
                purpose = prompt_data.get("purpose", "")
                guidelines = prompt_data.get("responseGuidelines", {})
                
                formatted_guidelines = ""
                if guidelines:
                    formatted_guidelines = "\nResponse Guidelines:"
                    for key, value in guidelines.items():
                        formatted_guidelines += f"\n- {key.replace('_', ' ').title()}: {value}"
                
                # Combine purpose and guidelines to form the core prompt for the LLM
                return f"""{purpose}{formatted_guidelines}"""
            
            # For simpler prompts, like the classifier, which might just have a direct 'prompt' field
            elif "prompt" in prompt_data:
                return prompt_data["prompt"]
            
            # Fallback for unexpected structures
            else:
                print(f"Warning: Could not find suitable prompt in {file_path}. Returning full JSON as string.")
                return json.dumps(prompt_data, indent=2)

    except FileNotFoundError:
        # Graceful fallback: return empty prompt if file missing
        return ""
    except json.JSONDecodeError:
        # Graceful fallback: return empty prompt if invalid JSON
        return ""

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
def ask_gemini(prompt):
    """Call Gemini with robust retries on transient errors (429/503) and timeouts.

    Retries are handled by tenacity with exponential backoff. We also surface
    concise error messages while preserving debug output for unexpected payloads.
    """
    load_dotenv() # Ensure .env is loaded before accessing GEMINI_API_KEY
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OFFLINE = os.getenv("RA9_OFFLINE", "false").lower() in ("1", "true", "yes")
    LLM_PROVIDER = os.getenv("RA9_LLM_PROVIDER", "gemini").lower()
    OLLAMA_MODEL = os.getenv("RA9_LLM_MODEL", "llama3:latest")

    # Offline or no key: return mock response to keep CLI/tests runnable
    if OFFLINE:
        return f"[mock-gemini] {prompt[:240]}"

    # Ollama provider path (local inference)
    if LLM_PROVIDER == "ollama":
        try:
            import requests
            host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
            url = os.getenv("OLLAMA_API_URL", f"{host}/api/generate")
            payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")
        except Exception as e:
            return f"[ollama-error] {e}"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    json_payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=json_payload,
            timeout=60
        )
        # Debugging: Print raw response content for all API calls.
        # This helps to see the exact structure from Gemini, especially if there's an error.
        print(f"[DEBUG - ask_gemini] Raw Gemini API Response (Status: {response.status_code}):\n{response.text}")

        # If Google returns JSON error payload with 200, detect and raise
        try:
            provisional_json = response.json()
            if isinstance(provisional_json, dict) and provisional_json.get("error"):
                # Simulate HTTP error to trigger retry
                raise requests.exceptions.HTTPError(provisional_json["error"].get("message", "API error"), response=response)
        except ValueError:
            # Non-JSON response; let raise_for_status handle it
            pass

        response.raise_for_status()
        response_json = provisional_json if 'provisional_json' in locals() else response.json()

        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            # Correctly extract and return the text content from the first candidate
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"DEBUG: Unexpected Gemini API response (no candidates): {response_json}")
            return "Error: Gemini API did not return candidates."

    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, 'status_code', None)
        # Retry on 429/503; surface other HTTP errors
        if status in (429, 503):
            print(f"HTTP {status} from Gemini. Retrying with backoff...\nResponse content: {getattr(e.response, 'text', '')}")
            raise
        # Fallback to mock on non-retryable errors if offline mode requested
        if OFFLINE:
            return f"[mock-gemini-http-{status}] {prompt[:240]}"
        print(f"HTTP Error: {e}")
        print(f"Response content: {getattr(e.response, 'text', '')}") # Ensure full response is always printed on HTTPError
        return f"Error: Failed to connect to Gemini API. Status code: {status}"
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        raise  # trigger retry
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
        raise  # trigger retry
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise  # trigger retry
    except KeyError as e:
        print(f"KeyError in Gemini API response: {e}")
        try:
            print(f"Full response: {response.json()}")
        except Exception:
            pass
        return "Error: Unexpected response structure from Gemini API."