from ra9.memory.memory_manager import get_memory_manager


def test_procedural_register_and_list():
    mm = get_memory_manager()
    pid = mm.register_procedural(path="procedural/hello.txt", name="hello", description="test", tags=["demo"]) 
    assert pid
    items = mm.list_procedural(tag="demo")
    assert any(i["id"] == pid for i in items)


def test_rebuild_index_runs():
    mm = get_memory_manager()
    n = mm.rebuild_index()
    assert isinstance(n, int)

