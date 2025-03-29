from pydantic import BaseModel, ConfigDict
from uuid import UUID, uuid4

class APISessionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session_id: str = None,
    model_loaded: bool = False,
    model: dict = None

def init():
    global sessions_db
    sessions_db = {}

def get_session_data(session_id: UUID):
    global sessions_db
    print(F"session_id: {session_id}")
    if session_id == None:
        session_id = uuid4()
        session_data = APISessionData()
        session_data.session_id = str(session_id)
        sessions_db[session_id] = session_data
    else:
        session_data = sessions_db[session_id]
        if session_data == None:
            session_data = APISessionData()
            session_data.session_id = str(session_id)
            sessions_db[session_id] = session_data
    return session_id, session_data

def update_session_data(session_id: UUID, session_data: APISessionData):
    global sessions_db
    session_data.session_id = str(session_id)
    sessions_db[session_id] = session_data
    return
