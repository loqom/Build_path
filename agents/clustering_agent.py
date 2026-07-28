# 1. Take pain_points from state
# 2. Send running callback
# 3. Embed each pain point using embeddings.py → add_documents()
# 4. Query ChromaDB to group similar ones
# 5. Use Groq LLM to name and summarize each cluster
# 6. Send completed callback
# 7. Return { **state, "clusters": clusters }


from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from services.node_callback import send_callback
from services.embeddings import add_documents
from models.schemas import AgentUpdate
from config.settings import settings
import json

llm=ChatGroq(api_key=settings.GROQ_API_KEY,model="llama-3.3-70b-versatile", temperature=0.4)

async def cluster_agent(state:dict)->dict:
    print("=== CLUSTERING STARTED ===")
    pain_points=state["pain_points"]
    sessionId=state["sessionId"]
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="cluster",
        status="running",
        message="Pushing into Vector database",
        isComplete=False
    ))
    texts = [f"{p['title']} {p['description']}" for p in pain_points]
    add_documents(texts=texts,metadatas=pain_points)
    prompt=f"""You are grouping developer pain points into themes.
    Below are {len(pain_points)} pain points collected from Reddit and GitHub.
    
    Group them into 5-8 meaningful clusters. For each cluster return:
    - name: short theme name
    - description: what this cluster is about
    - pain_points: list of titles that belong here
    - severity: overall severity (high/medium/low)
    
    Pain points:
    {json.dumps(pain_points, indent=2)}
    
    Return a JSON array only. No explanation, no markdown."""

    llm_response=llm.invoke([HumanMessage(content=prompt)])

    content = llm_response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    clusters = json.loads(content.strip())
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="clustering",
        status="completed",
        message=f"Formed {len(clusters)} clusters",
        output=json.dumps(clusters),
        isComplete=False
    ))

    return { **state, "clusters": clusters }
    