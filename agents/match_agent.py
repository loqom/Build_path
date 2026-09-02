# 1. Take clusters + techStack, skillLevel, timeAvailable, goal from state
# 2. Send running callback
# 3. Prompt Groq:
#    "Given this developer profile and these problem clusters,
#    score each cluster 0-100 on how buildable it is for them.
#    Return top 5 with matchScore, reasoning"
# 4. Parse response
# 5. Send completed callback
# 6. Return { **state, "matched": matched }


from langchain_core.messages import HumanMessage
from services.node_callback import send_callback
from services.llm import llm
from services.utils import parse_llm_json
from models.schemas import AgentUpdate
from config.settings import settings
import json

async def match_agent(state:dict)->dict:
    print("=== MATCH STARTED ===")
    techStack=state["techStack"]
    skillLevel=state["skillLevel"]
    clusters=state["clusters"]
    sessionId=state["sessionId"]
    timeAvailable=state["timeAvailable"]
    goal=state["goal"]
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="match",
        status="running",
        message="Finding perfect project for your domain",
        isComplete=False
    ))
    prompt=f"""
    You are a technical project advisor matching developer skills to problems.

    Developer Profile:
    - Tech Stack: {techStack}
    - Skill Level: {skillLevel}
    - Time Available: {timeAvailable}
    - Goal: {goal}

    Below are problem clusters found from real developer complaints online.
    Score each cluster from 0-100 based on:
    - How buildable it is given the developer's tech stack
    - How achievable it is given their skill level and time
    - How relevant it is to their goal (placement/freelance/startup/learning)

    For each cluster return:
    - name: cluster name
    - matchScore: 0-100
    - reasoning: why this matches or doesn't match the developer
    - buildability: easy / medium / hard
    - suggestedApproach: one line on how they could tackle this

    Problem Clusters:
    {json.dumps(clusters, indent=2)}

    Return top 5 clusters ranked by matchScore as a JSON array only. No explanation, no markdown.
    """
    llm_response = await llm.ainvoke([HumanMessage(content=prompt)])
    matched_clusters = parse_llm_json(llm_response.content)
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="match",
        status="completed",
        message="Matched top clusters",
        output=json.dumps(matched_clusters),
        isComplete=False
    ))
    return {**state, "matched": matched_clusters}