import time
from ra9.memory.memory_manager import get_memory_manager


def test_basic_stress_and_metrics_smoke():
    mm = get_memory_manager()
    # Insert a small batch (not full 10k to keep CI quick)
    n = 200
    for i in range(n):
        mm.write_memory("episodic", f"stress item {i} about graphs and trees", tags=["stress"], importance=0.5, consent=True)
    t0 = time.time()
    hits = mm.retrieve("graphs", k=10)
    dt = (time.time() - t0) * 1000.0
    # Expect retrieval under a modest threshold on dev machines
    assert dt < 1000.0
    # Metrics counters should update
    total = mm.get_metric("hits") + mm.get_metric("misses")
    assert total >= 1

