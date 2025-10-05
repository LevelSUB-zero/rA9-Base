import os
import json
from time import sleep

from fastapi.testclient import TestClient


def test_real_world_application_flow():
    # Use API surface to simulate a small real workflow
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)

    from ra9.server import app
    client = TestClient(app)

    # 1) Health and config
    r = client.get("/health")
    assert r.status_code == 200

    # 2) Write a memory with consent
    payload = {
        "type": "episodic",
        "text": "Kickoff notes for RA9: we'll build memory, councils, and pruning.",
        "tags": ["project", "kickoff"],
        "user_id": "u-api",
        "importance": 0.8,
        "consent": True
    }
    r = client.post("/memory/write", json=payload)
    assert r.status_code == 200
    mem_id = r.json().get("memoryId")
    assert mem_id

    # 3) Retrieve via API
    r = client.post("/memory/retrieve", json={"query": "kickoff RA9", "k": 5})
    assert r.status_code == 200
    results = r.json().get("results", [])
    assert isinstance(results, list)

    # 4) Consolidate and check facts created count
    r = client.post("/memory/consolidate")
    assert r.status_code == 200
    assert "createdFacts" in r.json()

    # 5) Working memory ops
    r = client.post("/memory/wm/add", json={"user_id": "u-api", "entries": ["alpha entry"], "cap": 5})
    assert r.status_code == 200
    r = client.get("/memory/wm", params={"user_id": "u-api", "cap": 5})
    assert r.status_code == 200
    wm = r.json().get("workingMemory", [])
    assert any("alpha" in s for s in wm)

    # 6) Event log/session
    r = client.post("/memory/event/write", json={"session_id": "s-1", "user_id": "u-api", "event_type": "user_query", "payload": {"text": "what is WM?"}, "importance": 0.5})
    assert r.status_code == 200
    r = client.get("/memory/session/s-1")
    assert r.status_code == 200
    assert len(r.json().get("events", [])) >= 1

    # 7) Prune + maintain
    r = client.post("/memory/prune")
    assert r.status_code == 200
    r = client.post("/memory/rebuild_index")
    assert r.status_code == 200

    # 8) Delete memory by id
    r = client.delete(f"/memory/{mem_id}")
    assert r.status_code == 200

