from fastapi import File, UploadFile
from src.services.exec import ExecService
from typing import List, Dict, Any
import uuid

class ExecController:
    def __init__(self):
        self.exec_service: ExecService = ExecService()
        self.session_manager: Dict[str, Any] = {}
        
    def create_session(self):
        session_id = str(uuid.uuid4())
        self.session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
        return session_id
        
    def execute_python(self, code_file_path: str):
        return self.exec_service.execute_python(code_file_path)

    def install_packages(self, session_id: str, session_manager, packages: List[str]):
        return self.exec_service.install_packages(session_id, session_manager, packages)

    def upload_file(self, session_id: str, session_manager, file: UploadFile = File(...)):
        return self.exec_service.upload_file(session_id, session_manager, file)

    def uninstall_packages(self, session_id: str, session_manager):
        return self.exec_service.uninstall_packages(session_id, session_manager)
