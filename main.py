from fastapi import FastAPI,BackgroundTasks
from models.schemas import PipelineRequest
from pipeline.graph import run_agent_pipeline
app=FastAPI()


@app.post("/pipeline/run")
async def run_pipeline(data: PipelineRequest,background_tasks:BackgroundTasks):
    background_tasks.add_task(run_agent_pipeline, data)
    return{
        "status":"received",
        "pipeline":"started"
    }
