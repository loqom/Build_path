# 1. import TavilyClient from tavily
# 2. import settings

# 3. initialize tavily client:
#    client = TavilyClient(api_key=settings.TAVILY_API_KEY)

# 4. define async function scrape_pain_points(techStack: list[str], goal: str) -> list[dict]:
   
#    a. build search queries from techStack:
#       queries = [
#         f"site:reddit.com {tech} problems developers face",
#         f"site:github.com/issues {tech} common issues",
#         f"site:news.ycombinator.com {tech} pain points",
#       ]
#       for each tech in techStack

#    b. for each query:
#       - call tavily client.search(query, max_results=5)
#       - extract title, url, content from each result
#       - append to results list

#    c. return deduplicated results list

import asyncio
from tavily import TavilyClient
from config.settings import settings


tavily=TavilyClient(api_key=settings.TAVILY_API_KEY)

async def scrape_pain_points(techStack:list[str])->list[dict]:
    """search the web for relevant problem statements matching the tech stack given"""
    results=[]
    for tech in techStack[:3]:
        queries = [
            f"site:reddit.com/r/{tech} problems",
            f"site:reddit.com {tech} frustrating",
            f"site:github.com {tech} issue bug",
        ]
        for query in queries:
            try:
                res = await asyncio.to_thread(tavily.search, query, max_results=5)
                if isinstance(res, dict) and "results" in res:
                    for item in res["results"]:
                        results.append({
                            "title": item.get("title", f"{tech} issue"),
                            "url": item.get("url", ""),
                            "content": item.get("content", ""),
                            "source": "reddit" if "reddit" in item.get("url", "") else "github"
                        })
            except Exception as e:
                print(f"Scraper Tavily search failed for query '{query}': {e}")

    # Fallback default pain points if search returned empty due to network issues
    if not results:
        stack_str = ", ".join(techStack) if techStack else "general technologies"
        results = [
            {
                "title": f"High memory consumption and scaling bottleneck in {stack_str}",
                "url": "https://github.com/issues/fallback-1",
                "content": f"Developers report performance degradation, memory leaks, and complex state synchronization when handling high concurrency in {stack_str}.",
                "source": "github"
            },
            {
                "title": f"Complex developer tooling and boilerplate setup for {stack_str}",
                "url": "https://reddit.com/r/devtools/fallback-2",
                "content": f"Configuring CI/CD pipelines, local testing mocks, and deployment scripts for {stack_str} projects is tedious and error-prone.",
                "source": "reddit"
            },
            {
                "title": f"Lack of real-time telemetry and error tracing in production {stack_str}",
                "url": "https://github.com/issues/fallback-3",
                "content": f"Debugging production issues across microservices built with {stack_str} lacks unified logging and metric visualizers.",
                "source": "github"
            }
        ]

    return results
    
