from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class QueryContext(BaseModel):
    queryId: str
    userId: str
    text: str
    mode: Literal["concise", "deep", "interactive"] = "concise"
    loopDepth: int = 1
    allowMemoryWrite: bool = False
    userPrefs: Dict[str, str] = Field(default_factory=dict)
    privacyFlags: Optional[Dict[str, bool]] = None
    risk_level: Optional[Literal["low", "medium", "high"]] = None
    latency_budget_ms: Optional[int] = None


class WorkerOutput(BaseModel):
    candidateId: str
    workerId: str
    text: str
    reasoningTrace: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None
    sources: List[str] = Field(default_factory=list)
    tokens: Optional[int] = None
    speculative: bool = True


class CouncilVote(BaseModel):
    voteId: str
    councilId: str
    candidateId: str
    axisScores: Dict[str, float] = Field(default_factory=dict)
    rationale: Optional[str] = None
    flags: List[str] = Field(default_factory=list)
    calibration: Optional[Dict[str, float]] = None


class AggregationResult(BaseModel):
    finalCandidateId: Optional[str] = None
    aggregatedScore: Optional[float] = None
    axisBreakdown: Dict[str, float] = Field(default_factory=dict)
    decision: Literal["select", "re_eval", "synthesize", "escalate", "fallback"] = "select"
    finalText: Optional[str] = None
    topK: Optional[List[str]] = None


class ContextWeights(BaseModel):
    weights: Dict[str, float]


class WorkerSelection(BaseModel):
    workers: List[str]


class CouncilConfig(BaseModel):
    councils: List[str]


class TrustSnapshot(BaseModel):
    council_axis_trust: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # councilId -> axis -> C_j,a
    worker_trust: Dict[str, float] = Field(default_factory=dict)  # workerId -> T_w


class AggregationInputs(BaseModel):
    candidates: List[WorkerOutput]
    votes: List[CouncilVote]
    context_weights: ContextWeights
    trust: TrustSnapshot
    lambda_sensitivity: float = 0.3
    beta_softmax: float = 6.0
    accept_threshold: float = 0.75
    margin_threshold: float = 0.08


