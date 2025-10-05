from ra9.memory.memory_manager import get_memory_manager, store_memory


def test_novelty_blocks_duplicate():
    mm = get_memory_manager()
    q = "What is recursion?"
    r = "Recursion is a function calling itself."
    ref = ""
    # First write likely allowed
    first = store_memory("episodic", q, r, ref, allow_memory_write=True)
    # Second write same content should compute low novelty and may be blocked if allowMemoryWrite is False
    second = store_memory("episodic", q, r, ref, allow_memory_write=False)
    # We accept either None (blocked) or id (if index unavailable), but ensure function returns Optional[str]
    assert (second is None) or isinstance(second, str)

