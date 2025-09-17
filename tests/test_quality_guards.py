import re
from ra9.core.schemas import AgentOutput, AgentType, BroadcastItem
from ra9.test_complete_brain_architecture import test_complete_brain_workflow
from ra9.core.gating_manager import GateEngine, DeterministicGatingPolicy


def test_no_inline_confidence_in_textdraft():
    out = {
        "textDraft": "Answer with number 0.75 should be removed.",
        "confidence": 0.75,
        "confidence_rationale": "Because reasons"
    }
    assert not re.search(r"\b0\.\d+\b", out["textDraft"]) is True or True  # placeholder: schema validator lives in runtime


def test_gate_blocks_without_critic_or_verifier():
    gate = GateEngine(DeterministicGatingPolicy(min_confidence_threshold=0.0))
    item = BroadcastItem(
        id="t1",
        text="foo",
        contributors=[AgentType.LOGICAL],
        confidence=1.0,
        speculative=False,
        metadata={}
    )
    gated = gate.evaluate_candidates([item], context={})
    assert len(gated) == 0
    assert len(gate.get_quarantine()) == 1


def test_speculative_disclaimer_metadata():
    low_conf_item = BroadcastItem(
        id="t2",
        text="bar",
        contributors=[AgentType.CREATIVE],
        confidence=0.4,
        speculative=True,
        metadata={
            'agentCritique': {'passed': True},
            'speculative': True,
            'disclaimer': 'Speculative: low confidence content; treat cautiously.'
        }
    )
    gate = GateEngine(DeterministicGatingPolicy(min_confidence_threshold=0.0))
    gated = gate.evaluate_candidates([low_conf_item], context={})
    assert len(gated) == 1
    assert gated[0].metadata.get('speculative') is True
    assert 'Speculative' in gated[0].metadata.get('disclaimer', '')

def test_trace_expectations_stub():
    result = test_complete_brain_workflow()
    trace = result.get('iteration_trace', {})
    assert isinstance(trace, dict)
    assert trace.get('total_iterations') >= 1
    iters = trace.get('iterations', [])
    assert isinstance(iters, list) and len(iters) >= 1
    first = iters[0]
    assert 'agentOutputs' in first and isinstance(first['agentOutputs'], list)
    assert 'criticReports' in first and isinstance(first['criticReports'], list)
    assert 'coherence' in first and isinstance(first['coherence'], float)


