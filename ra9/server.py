"""
RA9 Web Server.

This module provides a FastAPI-based web server for RA9.
"""

import json
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from .core.config import get_config
from .core.logger import get_logger
from .core.cli_workflow_engine import run_cli_workflow
from .memory.memory_manager import get_memory_manager, score_candidate
from .memory.jobs import consolidate_once, prune_once


# Pydantic models
class QueryRequest(BaseModel):
    text: str
    mode: str = "concise"
    loop_depth: int = 1
    allow_memory_write: bool = True
    user_id: Optional[str] = None


class QueryResponse(BaseModel):
    job_id: str
    result: Dict[str, Any]
    success: bool
    error: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="RA9 Cognitive Engine API",
    description="Ultra-Deep Cognitive Engine with Multi-Agent Architecture",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get logger
logger = get_logger("ra9.server")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RA9 Cognitive Engine API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    config = get_config()
    return {
        "status": "healthy",
        "configured": config.is_configured(),
        "memory_enabled": config.memory_enabled,
        "agents_available": True
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a single query."""
    
    config = get_config()
    if not config.is_configured():
        raise HTTPException(
            status_code=400,
            detail="No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY."
        )
    
    job_id = str(uuid.uuid4())
    
    try:
        # Create job payload
        job_payload = {
            "jobId": job_id,
            "text": request.text,
            "mode": request.mode,
            "loopDepth": request.loop_depth,
            "allowMemoryWrite": request.allow_memory_write,
            "userId": request.user_id or "api_user"
        }
        
        # Process query
        result = run_cli_workflow(job_payload)
        
        if "error" in result:
            return QueryResponse(
                job_id=job_id,
                result={},
                success=False,
                error=result["error"]
            )
        
        return QueryResponse(
            job_id=job_id,
            result=result,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def process_query_stream(request: QueryRequest):
    """Process a query with streaming response."""
    
    config = get_config()
    if not config.is_configured():
        raise HTTPException(
            status_code=400,
            detail="No API keys configured. Please set GEMINI_API_KEY or OPENAI_API_KEY."
        )
    
    job_id = str(uuid.uuid4())
    
    def generate_stream():
        try:
            # Create job payload
            job_payload = {
                "jobId": job_id,
                "text": request.text,
                "mode": request.mode,
                "loopDepth": request.loop_depth,
                "allowMemoryWrite": request.allow_memory_write,
                "userId": request.user_id or "api_user"
            }
            
            # Process query with streaming
            # This would need to be implemented in the workflow engine
            result = run_cli_workflow(job_payload)
            
            # Stream the result
            yield f"data: {json.dumps({'type': 'start', 'job_id': job_id})}\n\n"
            
            if "error" in result:
                yield f"data: {json.dumps({'type': 'error', 'error': result['error']})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.get("/config")
async def get_configuration():
    """Get current configuration."""
    config = get_config()
    return {
        "memory_enabled": config.memory_enabled,
        "max_iterations": config.max_iterations,
        "default_mode": config.default_mode,
        "enable_reflection": config.enable_reflection,
        "configured": config.is_configured()
    }


# -------------------------
# Memory endpoints (privacy-first minimal set)
# -------------------------

class MemorySearchRequest(BaseModel):
    query: str
    k: int = 6


@app.post("/memory/search")
async def memory_search(req: MemorySearchRequest):
    mm = get_memory_manager()
    hits = mm.retrieve(req.query, k=req.k)
    return {
        "hits": [
            {
                "memoryId": h.memory_id,
                "snippet": h.chunk_text,
                "distance": h.distance,
                "importance": h.importance,
                "timestamp": h.timestamp,
            }
            for h in hits
        ]
    }


class MemoryWriteRequest(BaseModel):
    type: str = "episodic"
    text: str
    tags: Optional[list] = None
    user_id: Optional[str] = None
    importance: float = 0.5
    consent: bool = False


@app.post("/memory/write")
async def memory_write(req: MemoryWriteRequest):
    if not req.consent:
        raise HTTPException(status_code=400, detail="Consent required for write.")
    mm = get_memory_manager()
    mem_id = mm.write_memory(req.type, req.text, tags=req.tags or [], user_id=req.user_id or "api_user", importance=req.importance, consent=True)
    return {"memoryId": mem_id}


@app.post("/memory/retrieve")
async def memory_retrieve(body: Dict[str, Any]):
    q = body.get("query") or ""
    k = int(body.get("k", 6))
    mm = get_memory_manager()
    hits = mm.retrieve(q, k=k)
    # unified scoring
    def _score(distance: float, importance: float, ts: int) -> float:
        return score_candidate(distance, importance, ts)
    # transform to output structure
    c = mm.conn.cursor()
    scored = []
    for h in hits:
        row = c.execute("SELECT raw_text, summary, importance, consent, privacy_level FROM memory_items WHERE id=?", (h.memory_id,)).fetchone()
        if not row:
            continue
        raw_text, summary, importance, consent, privacy = row
        if int(consent) != 1:
            continue
        if str(privacy or "low").lower() in ("high", "sensitive"):
            continue
        scored.append((
            _score(h.distance, importance, h.timestamp),
            {
                "rawText": raw_text,
                "summary": summary,
                "importance": float(importance or 0.0),
                "score": None,
            }
        ))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for s, item in scored:
        item["score"] = float(s)
        out.append(item)
    return {"results": out}


# Episodic event endpoints
class MemoryEventWriteRequest(BaseModel):
    session_id: str | None = None
    user_id: str | None = None
    event_type: str
    payload: Dict[str, Any]
    importance: float = 0.5


@app.post("/memory/event/write")
async def memory_event_write(req: MemoryEventWriteRequest):
    mm = get_memory_manager()
    sid = mm.log_event(
        event_type=req.event_type,
        payload=req.payload,
        user_id=req.user_id or "api_user",
        session_id=req.session_id,
        importance=req.importance,
    )
    return {"sessionId": sid}


@app.get("/memory/session/{session_id}")
async def memory_session_get(session_id: str, limit: int = 200):
    mm = get_memory_manager()
    events = mm.get_session_events(session_id, limit=limit)
    return {"sessionId": session_id, "events": events}


@app.get("/memory/tail")
async def memory_tail(k: int = 50):
    mm = get_memory_manager()
    return {"events": mm.get_tail(k=k)}


@app.post("/memory/session/delete")
async def memory_session_delete(body: Dict[str, Any]):
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    mm = get_memory_manager()
    n = mm.delete_session(session_id)
    return {"deleted": n}


# Working memory endpoints
@app.get("/memory/wm")
async def wm_get(user_id: str, cap: int = 7):
    mm = get_memory_manager()
    return {"userId": user_id, "workingMemory": mm.wm_get(user_id, cap=cap)}


class WMAddRequest(BaseModel):
    user_id: str
    entries: list[str]
    cap: int = 7


@app.post("/memory/wm/add")
async def wm_add(req: WMAddRequest):
    mm = get_memory_manager()
    mm.wm_add_entries(req.user_id, req.entries, cap=req.cap)
    return {"ok": True}


class WMClearRequest(BaseModel):
    user_id: str


@app.post("/memory/wm/clear")
async def wm_clear(req: WMClearRequest):
    mm = get_memory_manager()
    n = mm.wm_clear(req.user_id)
    return {"cleared": n}


# Procedural APIs
class ProceduralRegisterRequest(BaseModel):
    path: str
    name: str
    description: str | None = None
    tags: list[str] | None = None


@app.post("/memory/procedural/register")
async def procedural_register(req: ProceduralRegisterRequest):
    mm = get_memory_manager()
    pid = mm.register_procedural(req.path, req.name, description=req.description or "", tags=req.tags or [])
    return {"id": pid}


@app.get("/memory/procedural/list")
async def procedural_list(tag: str | None = None):
    mm = get_memory_manager()
    items = mm.list_procedural(tag=tag)
    return {"items": items}


@app.post("/memory/rebuild_index")
async def memory_rebuild_index():
    mm = get_memory_manager()
    n = mm.rebuild_index()
    return {"reindexed": n}


class MemoryDeleteRequest(BaseModel):
    memory_id: str


@app.post("/memory/delete")
async def memory_delete(req: MemoryDeleteRequest):
    mm = get_memory_manager()
    c = mm.conn.cursor()
    c.execute("DELETE FROM embeddings WHERE memory_id=?", (req.memory_id,))
    c.execute("DELETE FROM memory_items WHERE id=?", (req.memory_id,))
    mm.conn.commit()
    return {"deleted": True}


@app.delete("/memory/{memory_id}")
async def memory_delete_id(memory_id: str):
    mm = get_memory_manager()
    c = mm.conn.cursor()
    c.execute("DELETE FROM embeddings WHERE memory_id=?", (memory_id,))
    c.execute("DELETE FROM memory_items WHERE id=?", (memory_id,))
    mm.conn.commit()
    return {"deleted": True}


@app.post("/memory/consolidate")
async def memory_consolidate():
    n = consolidate_once()
    return {"createdFacts": n}


@app.post("/memory/prune")
async def memory_prune():
    n = prune_once()
    return {"pruned": n}


@app.get("/agents")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            {"name": "LogicAgent", "description": "Logical reasoning and analysis"},
            {"name": "EmotionAgent", "description": "Emotional intelligence and empathy"},
            {"name": "CreativeAgent", "description": "Creative thinking and ideation"},
            {"name": "StrategicAgent", "description": "Strategic planning and decision making"},
            {"name": "MetaCoherenceAgent", "description": "Meta-cognitive reflection and coherence"},
            {"name": "FeedbackAgent", "description": "Feedback and improvement suggestions"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
