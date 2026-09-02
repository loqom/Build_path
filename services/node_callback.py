import httpx
from config.settings import settings
from models.schemas import AgentUpdate

async def send_callback(update: AgentUpdate):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.NODE_CALLBACK_URL}/{update.sessionId}",
                json=update.model_dump(),
                timeout=10.0,
                headers={"X-Internal-Api-Key": settings.INTERNAL_API_KEY}
            )
            if resp.status_code != 200:
                print(f"[node_callback] Warning: Callback returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Callback failed for session {update.sessionId}: {e}")