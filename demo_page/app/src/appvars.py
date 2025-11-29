from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict
from uuid import UUID, uuid4

api_url = ""
sessions_db = {}

class SessionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session_id: str = None
    api_session_id: str = None
    created_at: datetime = None
    last_access: datetime = None

def init():
    global api_url, sessions_db
    api_url = ""
    sessions_db = {}

def get_session_data(session_id):
    global sessions_db
    clear_old_sessions()
    is_new_session = False
    print(F"session_id: {session_id}")
    if (session_id is None) or (not is_uuid(session_id)):
        is_new_session = True
        session_id = uuid4()
        session_data = SessionData()
        session_data.created_at = datetime.now()
        session_data.last_access = datetime.now()
        session_data.session_id = str(session_id)
    else:
        session_data = sessions_db.get(session_id)
        if session_data is None:
            is_new_session = True
            session_data = SessionData()
            session_data.created_at = datetime.now()
            session_data.session_id = str(session_id)
    session_data.last_access = datetime.now()
    sessions_db[session_id] = session_data
    return session_id, session_data, is_new_session

def update_session_data(session_id: UUID, session_data: SessionData):
    global sessions_db
    clear_old_sessions()
    session_data.session_id = str(session_id)
    session_data.last_access = datetime.now()
    sessions_db[session_id] = session_data
    return

def is_uuid(uuid_to_test, version=4):
    if uuid_to_test is None:
        return False
    uuid_str = str(uuid_to_test)
    try:
        # check for validity of Uuid
        _ = UUID(uuid_str, version=version)
    except ValueError:
        return False
    return True

def clear_old_sessions():
    old_sessions = []
    for session_id, session_data in sessions_db.items():
        if session_data.last_access < (datetime.now() - relativedelta(days=1)):
            old_sessions.append(session_id)
    for session_id in old_sessions:
        del sessions_db[session_id]
    return