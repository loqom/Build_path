# 1. Take pain_points from state
# 2. Send running callback
# 3. Embed each pain point using embeddings.py → add_documents()
# 4. Query ChromaDB to group similar ones
# 5. Use Groq LLM to name and summarize each cluster
# 6. Send completed callback
# 7. Return { **state, "clusters": clusters }


from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from services.scraper import scrape_pain_points
from services.node_callback import send_callback
from services.embeddings import add_documents
from models.schemas import AgentUpdate
from config.settings import settings
import json