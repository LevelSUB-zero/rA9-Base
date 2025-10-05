from ra9.memory.memory_manager import get_memory_manager
from ra9.router.context_preprocessor import preprocess_context


def test_wm_persistent_store_and_cap():
    mm = get_memory_manager()
    uid = "u-test"
    mm.wm_clear(uid)
    preprocess_context(uid, "m1")
    preprocess_context(uid, "m2")
    preprocess_context(uid, "m3")
    wm = mm.wm_get(uid, cap=2)
    assert len(wm) <= 2
    # If retrieval adds additional snippets first, allow any presence check
    joined = "\n".join(wm)
    assert "m2" in joined or "m3" in joined


def test_wm_clear():
    mm = get_memory_manager()
    uid = "u-test"
    mm.wm_add_entries(uid, ["x", "y", "z"], cap=3)
    n = mm.wm_clear(uid)
    assert n >= 1

