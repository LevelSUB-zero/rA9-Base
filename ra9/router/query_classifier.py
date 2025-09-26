import requests
from dotenv import load_dotenv
import os
from ra9.tools.tool_api import ask_gemini, load_prompt_from_json
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .context_preprocessor import preprocess_context

load_dotenv()

# Load the prompt for the Query Classifier
QUERY_CLASSIFIER_PROMPT = load_prompt_from_json("ra9/Prompts/ra9-v0.01 alpha/RA9QueryClassifierLayerPrompt.json")

@dataclass
class StructuredQuery:
    intent: str = "unknown"
    query_type: str = "unknown"
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    labels: List[str] = field(default_factory=list)
    label_confidences: Dict[str, float] = field(default_factory=dict)
    reasoning_depth: str = "auto"


class QueryClassifier:
    """Query classification system for RA9."""
    
    def __init__(self):
        self.classification_types = ["Emotional", "Logical", "Strategic", "Creative", "Factual", "Reflective"]
    
    def classify(self, text: str, memory_context: str = "", user_id: str = "") -> StructuredQuery:
        """Classify a query and return structured information."""
        return classify_query(text, memory_context, user_id)


def classify_query(text: str, memory_context: str = "", user_id: str = "") -> StructuredQuery:
    # Expand classification types to include Factual and Reflective
    classification_types = ["Emotional", "Logical", "Strategic", "Creative", "Factual", "Reflective"]
    
    # Collect pre-context and adjust prompt to request structured JSON output
    pre_context = preprocess_context(user_id or None, text)
    
    # Build the prompt with proper escaping
    classification_types_str = ", ".join(classification_types)
    memory_context_str = memory_context if memory_context else "No recent memory context available."
    pre_context_str = json.dumps(pre_context)
    
    prompt = f"""
{QUERY_CLASSIFIER_PROMPT}

You are an advanced AI query classifier. Your task is to analyze user input, integrate relevant memory context, and classify the query. Support multi-label routing: a query may map to multiple of: {classification_types_str}.

Additionally, you must extract the core intent, the main content, and any relevant metadata. Assign: (a) an overall confidence (0.0-1.0), (b) per-label confidences, and (c) a suggested reasoning_depth of "shallow" or "deep".

Memory Context:
{memory_context_str}

Pre-Context (user, time, recent memory, environment):
{pre_context_str}

User Query: {text}

Please provide your response in a JSON format with the following keys:
{{
    "intent": "main intent of the query (e.g., 'get_information', 'solve_problem', 'express_emotion')",
    "query_type": "primary type (one of {classification_types_str} )",
    "labels": ["zero or more secondary labels, subset of the same types"],
    "label_confidences": {{"Logical": 0.85, "Emotional": 0.65}},
    "content": "the core content or subject of the query",
    "metadata": {{
        "source": "user_input",
        "timestamp": "current_timestamp_isoformat",
        "context_summary": "brief summary of memory context if relevant"
    }},
    "confidence": "a float between 0.0 and 1.0 representing overall classification confidence",
    "reasoning_depth": "one of shallow | deep | auto"
}}
"""
    
    response_text = ask_gemini(prompt)

    if response_text.startswith("Error:"):
        print(f"Classifier Error: {response_text}")
        return StructuredQuery(intent="error", content=text, metadata={"error": response_text}, confidence=0.0)
    
    try:
        # Find the first '{' and last '}' to extract the JSON payload reliably
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_payload = response_text[json_start : json_end + 1]
        else:
            # If no valid JSON structure is found, consider the entire response as potentially malformed
            raise json.JSONDecodeError("No valid JSON structure found in response", response_text, 0)

        # Debugging: Print the exact JSON payload before parsing
        print(f"[DEBUG - classify_query] Attempting to parse JSON payload:\n{json_payload}")

        parsed_json = json.loads(json_payload)
        
        # Debugging: Print parsed_json to confirm its content
        print(f"[DEBUG - classify_query] Successfully parsed JSON: {parsed_json}")

        # Extract and validate fields, providing defaults if missing
        intent = parsed_json.get("intent", "unknown")
        query_type = parsed_json.get("query_type", "unknown").strip().lower()
        content = parsed_json.get("content", text)
        metadata = parsed_json.get("metadata", {})
        confidence = float(parsed_json.get("confidence", 0.0))
        labels = parsed_json.get("labels", []) or []
        if isinstance(labels, list):
            labels = [str(l).strip().lower() for l in labels]
        else:
            labels = []
        label_confidences = parsed_json.get("label_confidences", {}) or {}
        if isinstance(label_confidences, dict):
            safe_conf: Dict[str, float] = {}
            for k, v in label_confidences.items():
                try:
                    safe_conf[str(k).strip().lower()] = float(v)
                except Exception:
                    continue
            label_confidences = safe_conf
        else:
            label_confidences = {}
        reasoning_depth = parsed_json.get("reasoning_depth", "auto")
        
        return StructuredQuery(
            intent=intent,
            query_type=query_type,
            content=content,
            metadata=metadata,
            confidence=confidence,
            labels=labels,
            label_confidences=label_confidences,
            reasoning_depth=reasoning_depth
        )
    except json.JSONDecodeError as e:
        print(f"Warning: Classifier returned non-JSON response or invalid JSON: {response_text}. Error: {e}")
        return StructuredQuery(intent="parse_error", content=text, metadata={"raw_response": response_text, "error": str(e)}, confidence=0.0)
    except Exception as e:
        print(f"An unexpected error occurred during query classification: {e}")
        # Re-raise the exception to get a full traceback
        raise