from __future__ import annotations

from typing import List

from .schemas import WorkerOutput


DENYLIST = ["weapon", "bomb-making", "credit card", "ssn "]


def prefilter_candidates(candidates: List[WorkerOutput]) -> List[WorkerOutput]:
    filtered: List[WorkerOutput] = []
    for c in candidates:
        lower = c.text.lower()
        if any(term in lower for term in DENYLIST):
            # quarantine by marking speculative False; skip from evaluation
            c.speculative = False
            continue
        filtered.append(c)
    return filtered


