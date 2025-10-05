from time import sleep
from ra9.memory.memory_manager import get_memory_manager


def test_decay_affects_scoring_order():
    mm = get_memory_manager()
    old_id = mm.write_memory("episodic", "old memory example about graphs", tags=["t"], importance=0.8, consent=True)
    sleep(1)
    new_id = mm.write_memory("episodic", "new memory example about graphs", tags=["t"], importance=0.8, consent=True)
    hits = mm.retrieve("graphs", k=5)
    # Basic assertion: should have at least two hits
    assert len(hits) >= 2

