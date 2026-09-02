from fastapi import FastAPI,BackgroundTasks
from models.schemas import PipelineRequest
from pipeline.graph import run_agent_pipeline
app=FastAPI()

import asyncio

from services.node_callback import send_callback
from models.schemas import AgentUpdate

async def run_with_timeout(data):
    try:
        await asyncio.wait_for(run_agent_pipeline(data), timeout=120)
    except asyncio.TimeoutError:
        print(f"Pipeline timed out for session {data.sessionId}")
        await send_callback(AgentUpdate(
            sessionId=str(data.sessionId),
            agentName="system",
            status="failed",
            message="Pipeline execution timed out",
            isComplete=False
        ))
    except Exception as e:
        print(f"Pipeline failed for session {data.sessionId}: {e}")
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
    return { "status": "received", "pipeline": "started" }

