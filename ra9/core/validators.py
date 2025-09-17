import re
from .schemas import AgentOutput


_CONFIDENCE_INLINE_RE = re.compile(r"\b0\.\d+\b")


def validate_agent_output(out: AgentOutput) -> AgentOutput:
    """Ensure required fields exist and sanitize textDraft to avoid inline numeric confidence.
    If inline numeric confidence appears in textDraft, we remove isolated numeric tokens.
    """
    if not hasattr(out, 'confidence_rationale') or out.confidence_rationale is None:
        out.confidence_rationale = ""
    # Remove numeric confidence-like tokens from text_draft
    if _CONFIDENCE_INLINE_RE.search(out.text_draft or ""):
        out.text_draft = _CONFIDENCE_INLINE_RE.sub("[confidence elided]", out.text_draft)
    return out


