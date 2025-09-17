import re
from typing import Dict, Any
from .schemas import AgentOutput


def validate_agent_output_dict(out: Dict[str, Any]) -> Dict[str, Any]:
    assert "confidence" in out, "Missing confidence"
    assert "confidence_rationale" in out, "Missing confidence_rationale"
    assert not re.search(r"\b0\.\d+\b", out.get("textDraft", "")), "Numeric confidence found in textDraft"
    return out


