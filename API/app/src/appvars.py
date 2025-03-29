from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict
from uuid import UUID, uuid4

sessions_db = {}

class APISessionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session_id: str = None,
    model_loaded: bool = False,
    model: dict = None
    created_at: datetime = None
    last_access: datetime = None

def init():
    global sessions_db
    sessions_db = {}

def get_session_data(session_id: UUID):
    global sessions_db
    clear_old_sessions()
    print(F"session_id: {session_id}")
    if session_id == None:
        session_id = uuid4()
        session_data = APISessionData()
        session_data.created_at = datetime.now()
        session_data.session_id = str(session_id)
    else:
        session_data = sessions_db[session_id]
        if session_data is None:
            session_data = APISessionData()
            session_data.created_at = datetime.now()
            session_data.session_id = str(session_id)
    session_data.last_access = datetime.now()
    sessions_db[session_id] = session_data
    return session_id, session_data

def update_session_data(session_id: UUID, session_data: APISessionData):
    global sessions_db
    clear_old_sessions()
    session_data.last_access = datetime.now()
    session_data.session_id = str(session_id)
    sessions_db[session_id] = session_data
    return

def clear_old_sessions():
    for session_id, session_data in sessions_db.items():
        if session_data.last_access < (datetime.now() - relativedelta(days=1)):
            del sessions_db[session_id]
    return
