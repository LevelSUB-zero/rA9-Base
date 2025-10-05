from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, List, Tuple

from .schemas import (
    AggregationInputs,
    AggregationResult,
    CouncilVote,
    WorkerOutput,
)


def _safe_norm(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(max(v, 0.0) for v in weights.values())
    if total <= 0:
        return {k: 0.0 for k in weights}
    return {k: max(v, 0.0) / total for k, v in weights.items()}


def aggregate_axis_scores(
    candidate_id: str,
    axis: str,
    votes: List[CouncilVote],
    council_axis_trust: Dict[str, Dict[str, float]],
) -> float:
    numerator = 0.0
    denominator = 0.0
    for v in votes:
        if v.candidateId != candidate_id:
            continue
        score = v.axisScores.get(axis)
        if score is None:
            continue
        trust = council_axis_trust.get(v.councilId, {}).get(axis, 1.0)
        numerator += trust * score
        denominator += trust
    if denominator == 0.0:
        return 0.0
    return max(0.0, min(1.0, numerator / denominator))


def compute_candidate_scores(inputs: AggregationInputs) -> Tuple[Dict[str, float], Dict[str, Dict[str, float]]]:
    # Determine all axes present in votes
    axes = set()
    for v in inputs.votes:
        axes.update(v.axisScores.keys())

    # Axis-level aggregation per candidate (with council-axis trust influence)
    axis_breakdowns: Dict[str, Dict[str, float]] = {}
    for c in inputs.candidates:
        per_axis: Dict[str, float] = {}
        for axis in axes:
            base = aggregate_axis_scores(
                candidate_id=c.candidateId,
                axis=axis,
                votes=inputs.votes,
                council_axis_trust=inputs.trust.council_axis_trust,
            )
            # Trust influence already applied inside aggregate via council_axis_trust weights
            per_axis[axis] = base
        axis_breakdowns[c.candidateId] = per_axis

    # Context-weighted scores
    normalized_ctx = _safe_norm(inputs.context_weights.weights)
    base_scores: Dict[str, float] = {}
    for c in inputs.candidates:
        per_axis = axis_breakdowns.get(c.candidateId, {})
        score = 0.0
        for axis, w in normalized_ctx.items():
            score += w * per_axis.get(axis, 0.0)
        base_scores[c.candidateId] = score

    # Worker trust adjustment (reflective trust influence)
    adjusted_scores: Dict[str, float] = {}
    for c in inputs.candidates:
        worker_trust = inputs.trust.worker_trust.get(c.workerId, 1.0)
        adjusted = base_scores[c.candidateId] * (1.0 + inputs.lambda_sensitivity * (worker_trust - 1.0))
        adjusted_scores[c.candidateId] = adjusted

    # Normalization via softmax
    beta = inputs.beta_softmax
    max_a = max(adjusted_scores.values()) if adjusted_scores else 0.0
    exp_scores: Dict[str, float] = {}
    for cid, a in adjusted_scores.items():
        exp_scores[cid] = math.exp(beta * (a - max_a))
    z = sum(exp_scores.values()) or 1.0
    probs = {cid: exp_scores[cid] / z for cid in adjusted_scores}

    return probs, axis_breakdowns


def decide(inputs: AggregationInputs) -> AggregationResult:
    if not inputs.candidates:
        return AggregationResult(
            finalCandidateId=None,
            aggregatedScore=0.0,
            axisBreakdown={},
            decision="fallback",
            finalText=None,
        )

    probs, axis_breakdowns = compute_candidate_scores(inputs)
    ranked = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    top_id, top_p = ranked[0]
    second_p = ranked[1][1] if len(ranked) > 1 else 0.0

    if top_p >= inputs.accept_threshold and (top_p - second_p) >= inputs.margin_threshold:
        decision = "select"
        final_candidate = next(c for c in inputs.candidates if c.candidateId == top_id)
        return AggregationResult(
            finalCandidateId=top_id,
            aggregatedScore=top_p,
            axisBreakdown=axis_breakdowns.get(top_id, {}),
            decision=decision,
            finalText=final_candidate.text,
        )

    # If not accepted, request re-eval or synthesis depending on closeness
    decision = "synthesize" if (top_p - second_p) < inputs.margin_threshold else "re_eval"
    top_k = [cid for cid, _ in ranked[:2]]
    return AggregationResult(
        finalCandidateId=None,
        aggregatedScore=top_p,
        axisBreakdown=axis_breakdowns.get(top_id, {}),
        decision=decision,
        topK=top_k,
    )


