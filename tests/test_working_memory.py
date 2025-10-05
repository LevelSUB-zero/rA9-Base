from ra9.router.context_preprocessor import preprocess_context


def test_working_memory_persists_across_calls():
    ctx1 = preprocess_context("u1", "alpha one")
    ctx2 = preprocess_context("u1", "beta two")
    wm = ctx2.get("workingMemory", [])
    assert any("alpha one" in s for s in wm)
    assert any("beta two" in s for s in wm)

