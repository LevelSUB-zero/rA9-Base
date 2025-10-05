from __future__ import annotations

from typing import Dict, List

from .schemas import CouncilVote, WorkerOutput


def synthesize_top_k(candidates: List[WorkerOutput], votes: List[CouncilVote], top_ids: List[str]) -> str:
    # Simple concatenative synthesis MVP with brief rationale headlines
    id_to_candidate: Dict[str, WorkerOutput] = {c.candidateId: c for c in candidates}
    rationales: Dict[str, str] = {}
    for v in votes:
        if v.candidateId in top_ids and v.rationale:
            rationales.setdefault(v.candidateId, v.rationale)

    parts: List[str] = []
    for cid in top_ids:
        cand = id_to_candidate.get(cid)
        if not cand:
            continue
        rationale = rationales.get(cid, "")
        parts.append(f"Candidate {cid} (reason: {rationale}):\n{cand.text}")
    return "\n\n---\n\n".join(parts)


