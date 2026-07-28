from fastapi import FastAPI,BackgroundTasks
from models.schemas import PipelineRequest
from pipeline.graph import run_agent_pipeline
app=FastAPI()

import asyncio

async def run_with_timeout(data):
    try:
        await asyncio.wait_for(run_agent_pipeline(data), timeout=120)
    except asyncio.TimeoutError:
        print(f"Pipeline timed out for session {data.sessionId}")

@app.post("/pipeline/run")
async def run_pipeline(data: PipelineRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_with_timeout, data)
    return { "status": "received", "pipeline": "started" }


# @app.post("/pipeline/run")
# async def run_pipeline(data: PipelineRequest,background_tasks:BackgroundTasks):
#     background_tasks.add_task(run_agent_pipeline, data)
#     return{
#         "status":"received",
#         "pipeline":"started"
#     }
