# 1. Define the state schema (TypedDict)
# 2. Create StateGraph with that state
# 3. Add each agent as a node
# 4. Add edges connecting them in order:
#    Scout → Clustering → Match → Validator → Architect
# 5. Set entry point → Scout
# 6. Compile the graph
# 7. Export run_agent_pipeline(data) function that:
#    - builds initial state from PipelineRequest
#    - invokes the compiled graph

from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from agents.architect_agent import architect_agent
from agents.clustering_agent import clustering_agent
from agents.match_agent import match_agent
from agents.validator_agent import validator_agent
from agents.scout_agent import scout_agent


class PipelineState(TypedDict):
    sessionId: str
    techStack: list[str]
    skillLevel: str
    timeAvailable: str
    goal: str
    pain_points: list
    clusters: list
    matched: list
    validated: list
    projects: list

graph=StateGraph(PipelineState)

graph.add_node("scout", scout_agent)
graph.add_node("clustering", clustering_agent)
graph.add_node("match", match_agent)
graph.add_node("validator", validator_agent)
graph.add_node("architect", architect_agent)

graph.add_edge(START,"scout")
graph.add_edge("scout", "clustering")
graph.add_edge("clustering", "match")
graph.add_edge("match", "validator")
graph.add_edge("validator", "architect")
graph.add_edge("architect", END)

app=graph.compile()

async def run_agent_pipeline(data):
    initial_state = {
        "sessionId": str(data.sessionId),
        "techStack": data.techStack,
        "skillLevel": data.skillLevel,
        "timeAvailable": data.timeAvailable,
        "goal": data.goal,
        "pain_points": [],
        "clusters": [],
        "matched": [],
        "validated": [],
        "projects": []
    }
    await app.ainvoke(initial_state)