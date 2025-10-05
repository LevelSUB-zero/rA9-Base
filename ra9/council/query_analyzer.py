from __future__ import annotations

from typing import Dict, List, Tuple

from .schemas import ContextWeights, QueryContext, WorkerSelection


FAST_WORKERS = ["LogicalWorker_v1", "EmotionalWorker_v1"]
DEEP_WORKERS = ["LogicalWorker_v1", "EmotionalWorker_v1", "CreativeWorker_v1", "DomainWorker_v1"]


def analyze_query(ctx: QueryContext) -> Tuple[ContextWeights, WorkerSelection]:
    # Heuristic context weights, default to balanced
    weights: Dict[str, float] = {
        "accuracy": 0.4,
        "relevance": 0.2,
        "clarity": 0.2,
        "ethics": 0.2,
    }

    text_lower = ctx.text.lower()
    if any(k in text_lower for k in ["explain", "how", "what", "mechanism", "step"]):
        weights["clarity"] += 0.1
        weights["accuracy"] += 0.1
    if any(k in text_lower for k in ["medical", "legal", "finance", "safety", "risk"]):
        weights["accuracy"] += 0.1
        weights["ethics"] += 0.1

    # Normalize
    total = sum(weights.values()) or 1.0
    for k in list(weights.keys()):
        weights[k] = max(0.0, weights[k]) / total

    # Worker selection based on mode
    if ctx.mode in ("concise", "interactive"):
        workers = FAST_WORKERS
    else:
        workers = DEEP_WORKERS

    return ContextWeights(weights=weights), WorkerSelection(workers=workers)


