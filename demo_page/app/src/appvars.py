from pydantic import BaseModel, ConfigDict
from requests.cookies import RequestsCookieJar
from fastapi_sessions.backends.implementations import InMemoryBackend
from uuid import UUID, uuid4

class SessionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    api_session_id: str = None,
    api_cookies: RequestsCookieJar = None

backend = InMemoryBackend[UUID, SessionData]()

def init():
    global api_url
    api_url = ""

async def get_session_data(session_id: UUID):
    print(F"session_id: {session_id}")
    if session_id == None:
        session_id = uuid4()
        session_data = SessionData()
        await backend.create(session_id, session_data)
    else:
        session_data = await backend.read(session_id)
        if session_data == None:
            session_data = SessionData()
            _ = await backend.create(session_id, session_data)
    return session_id, session_data

