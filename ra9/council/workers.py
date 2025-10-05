from __future__ import annotations

import uuid
from typing import List

from .llm_client import LLMClient, LLMConfig
from .prompts import (
    LOGICAL_TEMPLATE,
    EMOTIONAL_TEMPLATE,
    CREATIVE_TEMPLATE,
    DOMAIN_TEMPLATE,
    build_prompt,
)
from .schemas import QueryContext, WorkerOutput
from .retrieval import web_search_snippets


def _cid() -> str:
    return f"c-{uuid.uuid4().hex[:8]}"


class BaseWorker:
    worker_id: str = "BaseWorker"
    template: str = ""

    def __init__(self, client: LLMClient | None = None, config: LLMConfig | None = None) -> None:
        self.client = client or LLMClient(config)

    def build_prompt(self, ctx: QueryContext) -> str:
        tone = ctx.userPrefs.get("tone", "neutral")
        return build_prompt(self.template, ctx.text, tone)

    def generate(self, ctx: QueryContext) -> WorkerOutput:
        prompt = self.build_prompt(ctx)
        text = self.client.complete(prompt)
        return WorkerOutput(
            candidateId=_cid(),
            workerId=self.worker_id,
            text=text,
            reasoningTrace=["prompt_assembled", "llm_complete"],
            confidence=0.7,
            sources=[],
            tokens=len(text.split()),
        )


class LogicalWorker(BaseWorker):
    worker_id = "LogicalWorker_v1"
    template = LOGICAL_TEMPLATE

    def generate(self, ctx: QueryContext) -> WorkerOutput:
        # Retrieve brief snippets to ground answer
        snippets = web_search_snippets(ctx.text, max_results=3)
        prompt = self.build_prompt(ctx)
        if snippets:
            joined = "\n".join([f"Source: {u}\nSnippet: {s}" for u, s in snippets])
            prompt = f"{prompt}\nUse these snippets to ground facts when useful:\n{joined}\n"
        text = self.client.complete(prompt)
        sources = [u for u, _ in snippets]
        return WorkerOutput(
            candidateId=_cid(),
            workerId=self.worker_id,
            text=text,
            reasoningTrace=["prompt_assembled", "retrieval_snippets", "llm_complete"],
            confidence=0.7,
            sources=sources,
            tokens=len(text.split()),
        )


class EmotionalWorker(BaseWorker):
    worker_id = "EmotionalWorker_v1"
    template = EMOTIONAL_TEMPLATE


class CreativeWorker(BaseWorker):
    worker_id = "CreativeWorker_v1"
    template = CREATIVE_TEMPLATE


class DomainWorker(BaseWorker):
    worker_id = "DomainWorker_v1"
    template = DOMAIN_TEMPLATE

    def generate(self, ctx: QueryContext) -> WorkerOutput:
        snippets = web_search_snippets(ctx.text, max_results=3)
        prompt = self.build_prompt(ctx)
        if snippets:
            joined = "\n".join([f"Source: {u}\nSnippet: {s}" for u, s in snippets])
            prompt = f"{prompt}\nDomain snippets:\n{joined}\n"
        text = self.client.complete(prompt)
        sources = [u for u, _ in snippets]
        return WorkerOutput(
            candidateId=_cid(),
            workerId=self.worker_id,
            text=text,
            reasoningTrace=["prompt_assembled", "retrieval_snippets", "llm_complete"],
            confidence=0.7,
            sources=sources,
            tokens=len(text.split()),
        )


def run_workers(worker_ids: List[str], ctx: QueryContext) -> List[WorkerOutput]:
    outputs: List[WorkerOutput] = []
    for wid in worker_ids:
        if wid == "LogicalWorker_v1":
            outputs.append(LogicalWorker().generate(ctx))
        elif wid == "EmotionalWorker_v1":
            outputs.append(EmotionalWorker().generate(ctx))
        elif wid == "CreativeWorker_v1":
            outputs.append(CreativeWorker().generate(ctx))
        elif wid == "DomainWorker_v1":
            outputs.append(DomainWorker().generate(ctx))
    return outputs


