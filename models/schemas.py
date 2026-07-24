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

class RoadmapWeek(BaseModel):
    week: int
    title: str
    tasks: list[str]

class ProjectFeatures(BaseModel):
    mvp: list[str]
    stretch: list[str]

class ProjectSpec(BaseModel):
    title: str
    oneLiner: str
    problemStatement: str
    proposedSolution: str
    techStack: list[str]
    matchScore: int        
    complexity: str       
    estimatedTime: str
    features: ProjectFeatures
    roadmap: list[RoadmapWeek]

class PipelineResult(BaseModel):
    sessionId: str
    projects: list[ProjectSpec]