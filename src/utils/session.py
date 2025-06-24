import uuid
from src.entities import SessionId

def get_session_id(request: SessionId):
    return request.session_id or str(uuid.uuid4())