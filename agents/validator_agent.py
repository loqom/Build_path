# 1. Take matched clusters from state
# 2. Send running callback
# 3. For each matched cluster:
#    - Tavily search → "existing tools for {cluster.name}"
#    - Pass results to Groq → "does a solution already exist?"
# 4. Filter out saturated ones
# 5. Send completed callback
# 6. Return { **state, "validated": validated }

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from services.node_callback import send_callback
from models.schemas import AgentUpdate
from config.settings import settings
from tavily import TavilyClient
import json

tavily=TavilyClient(api_key=settings.TAVILY_API_KEY)

llm=ChatGroq(api_key=settings.GROQ_API_KEY,model="llama-3.3-70b-versatile",temperature=0.4)

async def validate_agent(state:dict)->dict:
    print("=== validator STARTED ===")
    matched = state['matched']
    sessionId=state['sessionId']
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="validator",
        status="running",
        message="Validating clusters....",
        isComplete=False
    ))

    validated = []
    for cluster in matched:
        queries = [
           f"existing tools for {cluster.get('name', 'Unknown')} developers",
           f"saas product solving {cluster.get('name', 'Unknown')} problem",
           f"github open source {cluster.get('name', 'Unknown')} solution",
        ]

        results = []

        for query in queries:
            res=tavily.search(query,max_results=3)
            for item in res["results"]:
                results.append(f"{item['title']}: {item['content'][:200]}")


        prompt=f"""You are evaluating whether a developer problem is worth building a solution for.
            Problem Cluster: {cluster.get('name', 'Unknown')}
            Description: {cluster.get('description', cluster.get('reasoning', 'No description available'))}
            Existing solutions found online:
            {results}

            Evaluate this problem and return a JSON object with:
            - name: cluster name
            - isValid: true if a genuine gap exists, false if market is saturated
            - saturationLevel: low / medium / high
            - existingSolutions: list of existing tools/products found (max 3)
            - gapAnalysis: one paragraph on what gap still exists despite existing solutions
            - verdict: "build it" / "saturated" / "niche opportunity"

            Return JSON only. No explanation, no markdown."""

        llm_response=llm.invoke([(HumanMessage(content=prompt))])
        content = llm_response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        if result.get('isValid') == True:
            validated.append(result)
        
    await send_callback(AgentUpdate(
        sessionId=sessionId,
        agentName="validator",
        status="completed",
        message=f"Found {len(validated)} validated content",
        output=json.dumps(validated),
        isComplete=False
    ))
    
    return { **state, "validated": validated }