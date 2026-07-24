from fastapi import FastAPI,BackgroundTasks
from pydantic import BaseModel
app=FastAPI()

class requestpipeline(BaseModel):
    sessionId:str
    techStack:list[str]
    skillLevel:str
    timeAvailable:str 
    goal:str

@app.post("/pipeline/run")
async def run_pipeline(data: requestpipeline,background_tasks:BackgroundTasks):
    background_tasks.add_task(run_agent_pipeline, data)
    return{
        "status":"recieved",
        "pipeline":"started"
    }
