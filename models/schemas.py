from pydantic import BaseModel
from typing import Optional

class PipelineRequest(BaseModel):
    sessionId: str
    techStack: list[str]
    skillLevel: str
    timeAvailable: str
    goal: str

class AgentUpdate(BaseModel):
    sessionId: str
    agentName: str
    status: str       
    message: str
    output: Optional[str] = None
    isComplete: bool = False
    projects: Optional[list] = None