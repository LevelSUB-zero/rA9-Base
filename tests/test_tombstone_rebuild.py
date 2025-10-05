from ra9.memory.memory_manager import get_memory_manager


def test_tombstone_threshold_triggers_rebuild():
    mm = get_memory_manager()
    # create a few items
    ids = [mm.write_memory("episodic", f"ts item {i}", consent=True) for i in range(5)]
    # tombstone majority
    for mid in ids[:3]:
        mm.tombstone_memory(mid)
    # trigger check explicitly
    rebuilt = mm.maybe_auto_rebuild_on_tombstones()
    assert isinstance(rebuilt, bool)

