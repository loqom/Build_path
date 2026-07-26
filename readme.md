##ARCHITECTURE

buildpath-python/
├── main.py
├── requirements.txt
├── .env
├── agents/
│   ├── scout_agent.py
│   ├── clustering_agent.py
│   ├── match_agent.py
│   ├── validator_agent.py
│   └── architect_agent.py
├── pipeline/
│   └── graph.py
├── services/
│   ├── scraper.py
│   ├── embeddings.py
│   └── node_callback.py
├── models/
│   └── schemas.py
└── config/
    └── settings.py


##File Descriptions

main.py
FastAPI entry point. Has one endpoint POST /pipeline/run that receives the request from Node (sessionId, techStack, skillLevel, timeAvailable, goal), validates it using Pydantic schemas, and triggers the LangGraph pipeline in the background using BackgroundTasks. Returns { status: "started" } immediately so Node isn't kept waiting.

config/settings.py
Loads all environment variables using pydantic-settings. Every other file imports from here instead of calling os.getenv() directly. Keeps env access centralized.

models/schemas.py
Pydantic models for request/response validation. Defines what a valid pipeline request looks like, what an agent output looks like, and what the final project spec structure is. Acts as the type system for the entire microservice.

services/scraper.py
Contains all scraping logic. Uses Tavily API to search Reddit, GitHub Issues, and Hacker News for posts matching developer pain points. Returns raw list of posts with title, body, url, upvotes. Called by Scout Agent.


services/embeddings.py
Handles all ChromaDB operations. Initializes the ChromaDB client and collection, embeds text using Mistral's embedding model, stores embeddings, and queries for similar content. Called by Clustering Agent.


services/node_callback.py
Single function that POSTs agent updates back to Node.js. Called by every agent after it finishes. Uses httpx for async HTTP. Sends agentName, status, message, output, isComplete, and projects (on final call).

agents/scout_agent.py
First agent. Takes user's tech stack and goal as input. Calls scraper.py to fetch real posts from Reddit/GH/HN. Passes raw posts through Mistral LLM to extract and summarize genuine pain points. Returns structured list of pain points. Calls node_callback with status updates.

agents/clustering_agent.py
Second agent. Takes pain points from Scout. Embeds each one using embeddings.py, stores in ChromaDB. Groups semantically similar pain points into clusters using cosine similarity. Returns 5-8 themed clusters. Calls node_callback.

agents/match_agent.py
Third agent. Takes clusters + user's tech stack and skill level. Scores each cluster against the user profile using Mistral LLM — how buildable is this given their stack? Ranks clusters by match score. Returns top 3-5 matched problems. Calls node_callback.

agents/validator_agent.py
Fourth agent. Takes top matched problems. For each one, uses Tavily to search if solutions already exist, how saturated the space is, and whether there's still a gap. Filters out oversaturated ideas. Returns validated problem list. Calls node_callback.

agents/architect_agent.py
Fifth and final agent. Takes validated problems. For each one, prompts Mistral to generate a full project spec — title, oneLiner, problemStatement, proposedSolution, techStack, matchScore, complexity, estimatedTime, MVP features, stretch features, and week-by-week roadmap. Returns structured JSON matching Node's Project model exactly. Calls node_callback with isComplete: true and full projects array.

pipeline/graph.py
LangGraph StateGraph that wires all five agents in sequence. Defines the shared state object that passes data between agents. Each agent is a node, connected by edges in order: Scout → Clustering → Match → Validator → Architect. Entry point called by main.py.

requirements.txt
fastapi
uvicorn
python-dotenv
pydantic
pydantic-settings
langchain
langchain-mistralai
langgraph
chromadb
mistralai
tavily-python
httpx
beautifulsoup4
requests

Build order:
1. main.py
2. config/settings.py
3. models/schemas.py
4. services/node_callback.py
5. services/scraper.py
6. services/embeddings.py
7. agents/ (one by one)
8. pipeline/graph.py


Agents:
1. Scout Agent

Job: Go out to the internet and find real pain.

Takes the user's tech stack and goal. Uses scraper.py to fetch real posts from Reddit and GitHub. Then passes all that raw content through Mistral LLM to extract clean, structured pain points — filters out noise, keeps only genuine developer frustrations.

Input: techStack, skillLevel, goal, sessionId
Output: List of 20-30 structured pain points with title, description, source

2. Clustering Agent

Job: Group similar pain points together.

Takes the raw pain points from Scout. Embeds each one using Mistral embeddings via embeddings.py, stores them in ChromaDB. Then groups semantically similar ones into clusters — so "authentication is annoying", "JWT is confusing", "session management sucks" all become one cluster called something like "Auth & Session Management pain."

Input: List of pain points from Scout
Output: 5-8 named clusters, each containing related pain points

3. Match Agent

Job: Find which problems you can actually solve.

Takes the clusters and scores each one against the user's specific profile using Mistral LLM. Asks: "Given this person knows Node.js and React at intermediate level with 1 month available — how buildable is this problem for them?" Returns a ranked list with match scores.

Input: Problem clusters + user's techStack, skillLevel, timeAvailable, goal
Output: Top 3-5 clusters ranked by match score (0-100)

4. Validator Agent

Job: Make sure the idea is actually original.

Takes the top matched problems and for each one, uses Tavily to search if solutions already exist — checking GitHub, ProductHunt, existing SaaS tools. Filters out oversaturated ideas. Only passes through problems where a genuine gap still exists.

Input: Top 3-5 matched problems
Output: Validated problems with saturation level and gap assessment

5. Architect Agent

Job: Turn a validated problem into a complete build plan.

The final and heaviest agent. For each validated problem, prompts Mistral to generate a complete project spec — title, one-liner, problem statement, proposed solution, recommended tech stack, match score, complexity, estimated time, MVP features, stretch features, and a week-by-week roadmap with specific tasks. Output must exactly match the MongoDB Project schema so Node can save it directly.

Input: Validated problems + full user profile
Output: 3-5 complete ProjectSpec objects → sent to Node with isComplete: true