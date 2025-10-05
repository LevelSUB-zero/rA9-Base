from __future__ import annotations

from typing import Optional

from . import aggregator, councils, query_analyzer, safety, synthesis
from .schemas import AggregationInputs, AggregationResult, QueryContext
from .trust import TrustService
from .workers import run_workers


class CouncilPipeline:
    def __init__(self, trust: Optional[TrustService] = None) -> None:
        self.trust = trust or TrustService()
        # Initialize some neutral defaults for MVP
        for wid in [
            "LogicalWorker_v1",
            "EmotionalWorker_v1",
            "CreativeWorker_v1",
            "DomainWorker_v1",
        ]:
            self.trust.set_worker_trust(wid, 1.0)
        # seed council axis beta so trust can be computed
        for cid in ["AccuracyCouncil_v1", "ClarityCouncil_v1"]:
            self.trust.update_council_axis(cid, "accuracy", correct=True, decay=0.0)
            self.trust.update_council_axis(cid, "clarity", correct=True, decay=0.0)
            self.trust.update_council_axis(cid, "relevance", correct=True, decay=0.0)

    def run(self, ctx: QueryContext) -> AggregationResult:
        # 1-2. Analyze query
        context_weights, worker_sel = query_analyzer.analyze_query(ctx)

        # 3. Spawn workers
        self._emit_cli_event("council:workers:start", {"workers": worker_sel.workers})
        candidates = run_workers(worker_sel.workers, ctx)
        self._emit_cli_event("council:workers:done", {"count": len(candidates)})

        # 4. Safety pre-filter
        candidates = safety.prefilter_candidates(candidates)
        if not candidates:
            return AggregationResult(decision="fallback", finalText=None)

        # 5. Councils evaluate
        self._emit_cli_event("council:votes:start", {"candidates": len(candidates)})
        votes = councils.run_councils(ctx, candidates)
        self._emit_cli_event("council:votes:done", {"votes": len(votes)})

        # Log council votes as reflective memory (privacy permitting)
        try:
            from ra9.memory.memory_manager import store_reflective
            for v in votes:
                note = f"Council vote on {v.candidateId} axisScores={v.axisScores} rationale={v.rationale or ''}"
                store_reflective(note_text=note)
        except Exception:
            pass

        # 6-8. Aggregate and decide
        trust_snapshot = {
            "council_axis_trust": self.trust.get_council_axis_trust(),
            "worker_trust": self.trust.get_worker_trust(),
        }

        inputs = AggregationInputs(
            candidates=candidates,
            votes=votes,
            context_weights=context_weights,
            trust=TrustSnapshot(**trust_snapshot),
        )

        self._emit_cli_event("council:aggregate:start", {})
        decision = aggregator.decide(inputs)
        self._emit_cli_event("council:aggregate:done", {"decision": decision.decision, "topK": decision.topK or []})

        # 9. Synthesis if needed
        if decision.decision == "synthesize" and decision.topK:
            decision.finalText = synthesis.synthesize_top_k(candidates, votes, decision.topK)

        # 10. Safety gate placeholder (no-op in MVP)

        return decision

    def _emit_cli_event(self, event: str, data: dict) -> None:
        try:
            from ra9.core.enhanced_cli_ui import get_cli
            cli = get_cli()
            if hasattr(cli, "emit_event"):
                cli.emit_event(event, data)
        except Exception:
            pass


