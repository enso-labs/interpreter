from pydantic import BaseModel
from typing import Dict, List

class SessionId(BaseModel):
    session_id: str = None

class CodeExecution(SessionId):
    code: str
    env: Dict[str, str] = {}

class PackageInstall(SessionId):
    packages: List[str]
    
class PythonResult(BaseModel):
    status: str
    output: str
    errors: str