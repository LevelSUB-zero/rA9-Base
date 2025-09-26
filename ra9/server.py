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
