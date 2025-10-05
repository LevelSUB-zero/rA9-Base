from __future__ import annotations

import uuid
from typing import Dict, List

from .schemas import CouncilVote, QueryContext, WorkerOutput


def _vid() -> str:
    return f"v-{uuid.uuid4().hex[:8]}"


def evaluate_accuracy(ctx: QueryContext, candidate: WorkerOutput) -> CouncilVote:
    # Simple heuristic: logical and domain workers get higher base accuracy
    base = 0.8 if candidate.workerId in ("LogicalWorker_v1", "DomainWorker_v1") else 0.6
    return CouncilVote(
        voteId=_vid(),
        councilId="AccuracyCouncil_v1",
        candidateId=candidate.candidateId,
        axisScores={"accuracy": base, "relevance": 0.7},
        rationale="Heuristic accuracy estimate based on worker type.",
        flags=[],
    )


def evaluate_clarity(ctx: QueryContext, candidate: WorkerOutput) -> CouncilVote:
    length = len(candidate.text.split())
    clarity = 0.85 if length <= 120 else 0.7
    return CouncilVote(
        voteId=_vid(),
        councilId="ClarityCouncil_v1",
        candidateId=candidate.candidateId,
        axisScores={"clarity": clarity, "relevance": 0.7},
        rationale="Shorter responses deemed clearer in MVP.",
        flags=[],
    )


def run_councils(ctx: QueryContext, candidates: List[WorkerOutput]) -> List[CouncilVote]:
    votes: List[CouncilVote] = []
    for c in candidates:
        votes.append(evaluate_accuracy(ctx, c))
        votes.append(evaluate_clarity(ctx, c))
    return votes


