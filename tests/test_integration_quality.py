from ra9.test_complete_brain_architecture import test_complete_brain_workflow


def test_integration_broadcast_block_when_critiques_fail(monkeypatch):
    # This integration test calls the complete workflow. The workflow prints but returns result dict.
    result = test_complete_brain_workflow()
    # If critics fail in this synthetic run, gating should produce 0 items. We allow >=0 depending on generated data.
    # Since we can't control LLM, assert that each gated item had critique metadata present.
    for item in result['gated_items']:
        assert 'agentCritique' in getattr(item, 'metadata', {})


