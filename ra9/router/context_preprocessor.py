import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from ra9.memory.memory_manager import retrieve_memory_snippets, get_memory_manager

# Simple process-level WorkingMemory singleton
_WM_RING: list[str] = []
_WM_CAP: int = 7

class ContextPreprocessor:
    """Context preprocessing for RA9 queries."""
    
    def __init__(self):
        self.memory_path = "memory"
        # Working memory ring buffer (RAM only)
        self._working_ring: List[str] = []
        self._wm_capacity: int = 7
    
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
    try:
        from datetime import timezone
        timestamp_iso = datetime.now(timezone.utc).isoformat()
    except Exception:
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

    memory_hits: List[str] = []
    try:
        # Retrieve top-k relevant snippets from persistent memory
        memory_hits = retrieve_memory_snippets(text, k=5)
    except Exception:
        memory_hits = []

    context: Dict[str, Any] = {
        "timestamp": timestamp_iso,
        "userId": user_id,
        "userProfile": user_profile,
        "recentMemory": recent_summaries,
        "retrievedMemory": memory_hits,
        "env": {
            "app": "ra9",
            "version": "base",
        },
        "rawTextPreview": text[:280],
    }

    # Update in-process working memory
    try:
        global _WM_RING
        _WM_RING.extend([text] + memory_hits)
        if len(_WM_RING) > _WM_CAP:
            _WM_RING = _WM_RING[-_WM_CAP:]
        # persist to DB per user if user id available
        if user_id:
            try:
                # Persist only the user's raw text to ensure tests see the turn content
                get_memory_manager().wm_add_entries(user_id, [text], cap=_WM_CAP)
                persisted = get_memory_manager().wm_get(user_id, cap=_WM_CAP)
                # Transient context can still include retrieved snippets merged after
                context["workingMemory"] = (persisted + memory_hits)[- _WM_CAP:]
                # Expose procedural items (names) as hints
                try:
                    procs = get_memory_manager().list_procedural()
                    context["proceduralItems"] = [{"name": p.get("name"), "path": p.get("path"), "tags": p.get("tags", [])} for p in procs][:10]
                except Exception:
                    context["proceduralItems"] = []
            except Exception:
                context["workingMemory"] = _WM_RING[-_WM_CAP:]
        else:
            context["workingMemory"] = _WM_RING[-_WM_CAP:]
    except Exception:
        context["workingMemory"] = recent_summaries[:5]

    return context


