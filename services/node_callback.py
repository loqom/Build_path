import httpx
from config.settings import settings
from models.schemas import AgentUpdate

async def send_callback(update: AgentUpdate):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.NODE_CALLBACK_URL}/{update.sessionId}",
                json=update.model_dump(),
                timeout=10.0
            )
    except Exception as e:
        print(f"Callback failed for session {update.sessionId}: {e}")