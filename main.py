from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import asyncio
import logging

from models.schemas import PipelineRequest, AgentUpdate
from pipeline.graph import run_agent_pipeline
from services.node_callback import send_callback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

allowed_origins = [
    "http://localhost:3001",
    "http://localhost:5000",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5000",
    "http://backend:3001", 
    os.getenv("BACKEND_URL", "http://localhost:3001")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_with_timeout(data):
    try:
        await asyncio.wait_for(run_agent_pipeline(data), timeout=300)
    except asyncio.TimeoutError:
        logger.error(f"Pipeline timed out for session {data.sessionId}")
        await send_callback(AgentUpdate(
            sessionId=str(data.sessionId),
            agentName="system",
            status="failed",
            message="Pipeline execution timed out",
            isComplete=False
        ))
    except Exception as e:
        logger.error(f"Pipeline failed for session {data.sessionId}: {e}")
        await send_callback(AgentUpdate(
            sessionId=str(data.sessionId),
            agentName="system",
            status="failed",
            message=f"Pipeline error: {str(e)}",
            isComplete=False
        ))

@app.post("/pipeline/run")
async def run_pipeline(data: PipelineRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_with_timeout, data)
    return {"status": "received", "pipeline": "started"}

@app.get("/health")
async def health():
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "service": "buildpath-python"}
    )

@app.get("/")
async def root():
    return JSONResponse(
        status_code=200,
        content={"message": "BuildPath Python Microservice running"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  
        port=int(os.getenv("PORT", 5000)),
        log_level="info"
    )