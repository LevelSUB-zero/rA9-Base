from __future__ import annotations

from typing import Dict


LOGICAL_TEMPLATE = (
    "ROLE: LogicalWorker\n"
    "INSTRUCTIONS:\n"
    "- Generate a factual, step-by-step answer.\n"
    "- Audience/tone: {tone}.\n"
    "- Keep it concise and structured.\n"
    "RETURN ONLY THE ANSWER TEXT.\n\n"
    "QUERY: {query}\n"
)


EMOTIONAL_TEMPLATE = (
    "ROLE: EmotionalWorker\n"
    "INSTRUCTIONS:\n"
    "- Provide supportive, empathetic phrasing.\n"
    "- Avoid factual claims unless grounded.\n"
    "- Audience/tone: {tone}.\n"
    "RETURN ONLY THE ANSWER TEXT.\n\n"
    "QUERY: {query}\n"
)


CREATIVE_TEMPLATE = (
    "ROLE: CreativeWorker\n"
    "INSTRUCTIONS:\n"
    "- Explain via analogy or story.\n"
    "- Keep it accurate and age-appropriate.\n"
    "RETURN ONLY THE ANSWER TEXT.\n\n"
    "QUERY: {query}\n"
)


DOMAIN_TEMPLATE = (
    "ROLE: DomainWorker\n"
    "INSTRUCTIONS:\n"
    "- Provide domain-specific considerations and caveats.\n"
    "- Cite sources when making claims.\n"
    "RETURN ONLY THE ANSWER TEXT.\n\n"
    "QUERY: {query}\n"
)


def build_prompt(template: str, query: str, tone: str) -> str:
    return template.format(query=query, tone=tone)


