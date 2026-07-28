# 1. Scout Agent

# Job: Go out to the internet and find real pain.

# Takes the user's tech stack and goal. Uses scraper.py to fetch real posts from Reddit and GitHub. Then passes all that raw content through Mistral LLM to extract clean, structured pain points — filters out noise, keeps only genuine developer frustrations.

# Input: techStack, skillLevel, goal, sessionId
# Output: List of 20-30 structured pain points with title, description, source

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from services.scraper import scrape_pain_points
from services.node_callback import send_callback
from models.schemas import AgentUpdate
from config.settings import settings
import json

llm=ChatGroq(api_key=settings.GROQ_API_KEY,model="llama-3.3-70b-versatile", temperature=0.4)
async def scout_agent(state:dict)->dict:
    print("=== SCOUT STARTED ===")
    techStack=state["techStack"]
    sessionId=state["sessionId"]
    goal=state["goal"]

    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="scout",
        status="running",
        message="Scraping Reddit and GitHub for pain points...",
        isComplete=False
    ))

    response=scrape_pain_points(techStack,goal)

    combined="\n\n".join([
        f"Title:{p['title']}\nContent:{p['content']}"
        for p in response
    ])

    prompt=f"""
    You are analyzing developer forum posts and GitHub issues.
    Extract genuine developer pain points from the content below.
    
    For each pain point return a JSON object with:
    - title: short problem name
    - description: what frustrates developers about this
    - severity: high / medium / low
    - source_tech: which technology this relates to
    
    Content:
    {combined}
    
    Return a JSON array only. No explanation, no markdown."""


    llm_response=llm.invoke([HumanMessage(content=prompt)])

    content = llm_response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    pain_points = json.loads(content.strip())
    
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="scout",
        status="completed",
        message=f"Found {len(pain_points)} pain points",
        output=json.dumps(pain_points),
        isComplete=False
    ))

    return { **state, "pain_points": pain_points }

