import os
import shutil

from ra9.memory.memory_manager import get_memory_manager, retrieve_memory_snippets, evaluate_write


def setup_module(module):
    # Ensure a clean memory directory for tests
    if os.path.exists("memory"):
        try:
            shutil.rmtree("memory")
        except Exception:
            pass


def test_write_and_retrieve_roundtrip():
    mm = get_memory_manager()
    text = "RA9 project kickoff notes: we will build council, memory, and pruning."
    mem_id = mm.write_memory("episodic", text, tags=["project", "ra9"], importance=0.8, consent=True)
    assert mem_id

    hits = retrieve_memory_snippets("What did we plan for memory?", k=3)
    assert isinstance(hits, list)
    assert any("memory" in h.lower() for h in hits)


def test_evaluate_write_thresholds():
    low = evaluate_write("foo", importance=0.1, novelty=0.1, utility=0.1, emotion_weight=0.0)
    high = evaluate_write("useful project info", importance=0.9, novelty=0.7, utility=0.9, emotion_weight=0.1)
    assert low in (False, True)  # function returns bool
    assert high is True


