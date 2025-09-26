import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class ContextPreprocessor:
    """Context preprocessing for RA9 queries."""
    
    def __init__(self):
        self.memory_path = "memory"
    
    def preprocess(self, user_id: Optional[str], text: str) -> Dict[str, Any]:
        """Preprocess context for a query."""
        return preprocess_context(user_id, text)


def _read_json_file(path: str) -> Any:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def _read_episodic_tail(path: str, limit: int = 10) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return entries
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        for line in lines:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []
    return entries


def preprocess_context(user_id: Optional[str], text: str) -> Dict[str, Any]:
    """
    Collect lightweight context before classification.
    - Current timestamp
    - User profile (if present)
    - Recent episodic memory summaries
    - Basic environment flags
    """
    timestamp_iso = datetime.utcnow().isoformat()

    user_info_path = os.path.join("memory", "user_info.json")
    episodic_log_path = os.path.join("memory", "episodic_log.jsonl")

    user_profile = _read_json_file(user_info_path) or {}
    recent_episodes = _read_episodic_tail(episodic_log_path, limit=5)

    recent_summaries: List[str] = []
    for e in recent_episodes:
        summary = e.get("response") or e.get("query") or ""
        if isinstance(summary, str) and summary.strip():
            recent_summaries.append(summary.strip()[:400])

    context: Dict[str, Any] = {
        "timestamp": timestamp_iso,
        "userId": user_id,
        "userProfile": user_profile,
        "recentMemory": recent_summaries,
        "env": {
            "app": "ra9",
            "version": "base",
        },
        "rawTextPreview": text[:280],
    }

    return context


