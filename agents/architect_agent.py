# 1. Take validated from state
# 2. Send running callback
# 3. For each validated cluster → prompt Groq to generate full project spec
# 4. Parse each spec into ProjectSpec structure
# 5. Collect all projects
# 6. Send final callback with isComplete=True + projects array
# 7. Return { **state, "projects": projects }

from config.settings import settings
from services.node_callback import send_callback
from services.llm import llm
from services.utils import parse_llm_json
from models.schemas import AgentUpdate
from langchain_core.messages import HumanMessage
import json

async def architect_agent(state:dict)->dict:
    print("=== architect STARTED ===")
    validated=state["validated"]
    sessionId=state["sessionId"]
    techStack=state["techStack"]
    skillLevel=state["skillLevel"]
    timeAvailable=state["timeAvailable"]
    goal=state["goal"]

    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="architect",
        status="running",
        message="Compiling everything ....",
        isComplete=False
    ))

    
    projects=[]
    for cluster in validated:

        prompt=f"""you are a senior software architect generating a complete project specification.

        Developer Profile:
        - Tech Stack: {techStack}
        - Skill Level: {skillLevel}
        - Time Available: {timeAvailable}
        - Goal: {goal}

        Validated Problem:
        - Name: {cluster.get('name', 'Unknown')}
        - Description: {cluster.get('gapAnalysis', cluster.get('reasoning', 'No description'))}
        - Verdict: {cluster.get('verdict', '')}
        - Gap Analysis: {cluster.get('gapAnalysis', '')}

        Generate a complete project specification and return a JSON object with exactly these fields:
        - title: creative project name
        - sector: one of "DevTools", "AI/ML", "Fintech", "Web3", "Healthtech", "E-Commerce", "Security" — pick the best match
        - oneLiner: one sentence describing what it does
        - problemStatement: 2-3 sentences on the real problem this solves
        - proposedSolution: 2-3 sentences on how the project solves it
        - techStack: list of specific technologies to use (based on developer's stack)
        - matchScore: integer 0-100 based on how well it matches developer profile
        - complexity: "easy" or "medium" or "hard"
        - estimatedTime: realistic time estimate e.g. "3 weeks", "1 month"
        - features: {{
            "mvp": list of 4-5 core features for v1,
            "stretch": list of 3-4 future features
        }}
        - roadmap: list of weekly objects like {{
            "week": 1,
            "title": "short milestone title",
            "tasks": list of 3-4 specific tasks for that week
        }}

        Make the roadmap fit within {timeAvailable}.
        Make the tech stack use what the developer already knows: {techStack}.

        Return JSON only. No explanation, no markdown."""

        llm_response = await llm.ainvoke([HumanMessage(content=prompt)])

        final_projects = parse_llm_json(llm_response.content)        
        if isinstance(final_projects, dict):
            projects.append(final_projects)
        elif isinstance(final_projects, list):
            projects.extend(final_projects)


    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="architect",
        status="completed",
        message="Finished the pipeline",
        output=json.dumps(projects),
        isComplete=True,
        projects=projects
    ))

    return { **state, "projects": projects }