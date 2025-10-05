from ra9.memory.memory_manager import get_memory_manager


def test_event_roundtrip():
    mm = get_memory_manager()
    sid = mm.log_event("user_query", {"text": "hello"}, user_id="u1")
    assert sid
    mm.log_event("worker_draft", {"text": "draft"}, user_id="u1", session_id=sid)
    events = mm.get_session_events(sid)
    assert len(events) >= 2
    tail = mm.get_tail(k=5)
    assert isinstance(tail, list)
    deleted = mm.delete_session(sid)
    assert deleted >= 2

