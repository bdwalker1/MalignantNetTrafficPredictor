from pydantic import BaseModel, ConfigDict
from uuid import UUID, uuid4

class SessionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    session_id: str = None
    api_session_id: str = None

def init():
    global api_url, sessions_db
    api_url = ""
    sessions_db = {}

def get_session_data(session_id):
    global sessions_db
    is_new_session = False
    print(F"session_id: {session_id}")
    if (session_id == None) or (not is_uuid(session_id)):
        is_new_session = True
        session_id = uuid4()
        session_data = SessionData()
        session_data.session_id = str(session_id)
        sessions_db[session_id] = session_data
    else:
        session_data = sessions_db.get(session_id)
        if session_data == None:
            is_new_session = True
            session_data = SessionData()
            session_data.session_id = str(session_id)
            sessions_db[session_id] = session_data
    return session_id, session_data, is_new_session

def update_session_data(session_id: UUID, session_data: SessionData):
    global sessions_db
    session_data.session_id = str(session_id)
    sessions_db[session_id] = session_data
    return

def is_uuid(uuid_to_test, version=4):
    if uuid_to_test == None:
        return False
    uuid_str = str(uuid_to_test)
    try:
        # check for validity of Uuid
        uuid_obj = UUID(uuid_str, version=version)
    except ValueError:
        return False
    return True