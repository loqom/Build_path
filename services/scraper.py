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

import os
from tavily import TavilyClient
from config.settings import settings
from langchain.tools import tool


tavily=TavilyClient(api_key=settings.TAVILY_API_KEY)

def scrape_pain_points(techStack:list[str],goal:str)->list[dict]:
    """search the web for relevant problem statements matching the tech stack given"""
    results=[]
    for tech in techStack[:3]:

        queries = [
            f"site:reddit.com/r/{tech} problems",
            f"site:reddit.com {tech} frustrating",
            f"site:github.com {tech} issue bug",
        ]
        for query in queries:
            res=tavily.search(query,max_results=5)
            for item in res["results"]:
                results.append({
                    "title": item["title"],
                    "url": item["url"],
                    "content": item["content"],
                    "source": "reddit" if "reddit" in item["url"] else "github"
                })
    return results
    
