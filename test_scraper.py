import asyncio
from services.scraper import scrape_pain_points

async def main():
    result = await scrape_pain_points.ainvoke({
        "techStack": ["FastAPI"],
        "goal": "Build an AI backend"
    })

    for r in result:
        print("-" * 80)
        print(r["title"])
        print(r["url"])
        print(r["content"])

asyncio.run(main())