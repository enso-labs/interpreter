import os
import shutil
import subprocess

from typing import Dict, Any, List

from fastapi import File, HTTPException, UploadFile
from src.config import Config
from src.entities import *

class ExecService:
    def __init__(self):
        self.api_url = Config.API_URL
        
    ## Write the code to a temporary file
    # @param session_id: str
    # @param code: str
    # @return code_file_path: str
    def write_code(self, session_id: str, code: str):
        # Create session directory if it doesn't exist
        session_dir = f"/tmp/{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        # Write code to a temporary file
        code_file_path = f"{session_dir}/temp_code.py"
        with open(code_file_path, "w") as code_file:
            code_file.write(code)
        return code_file_path

    ## Execute the code
    # @param code_file_path: str
    # @return PythonResult
    def execute_python(self, code_file_path: str):
        result = subprocess.run(["python", code_file_path], capture_output=True, text=True)
        if result.returncode == 0:
            return PythonResult(status="success", output=result.stdout, errors=result.stderr)
        else:
            return PythonResult(status="error", output=result.stdout, errors=result.stderr)

    ## Install the packages
    # @param session_id: str
    # @param session_manager: Dict[str, Any]
    # @return PythonResult
    def install_packages(
        self, 
        session_id: str, 
        session_manager: Dict[str, Any],
        packages: List[str]
    ):
        # Install packages if any are provided and not already installed
        for package in packages:
            if package not in session_manager[session_id]["packages"]:
                subprocess.check_call([f"pip install {package}"], shell=True)
                session_manager[session_id]["packages"].add(package)
                
        return PackageInstall(
            status="success",
            installed_packages=list(session_manager[session_id]["packages"]),
        )
        
    ## Terminate the session
    # @param session_id: str
    # @return PythonResult
    def uninstall_packages(self, session_id: str, session_manager: Dict[str, Any]):
        try:
            # Uninstall packages
            packages_to_remove = " ".join(session_manager[session_id]["packages"])
            if packages_to_remove:
                subprocess.check_call([f"pip uninstall -y {packages_to_remove}"], shell=True)

            # Remove files and directory
            for file_path in session_manager[session_id]["files"]:
                if os.path.exists(file_path):
                    os.remove(file_path)

            session_dir = f"/tmp/{session_id}"
            if os.path.exists(session_dir):
                os.rmdir(session_dir)

            # Clean up session
            del session_manager[session_id]
            
            return {"status": "success", "message": f"Session {session_id} terminated successfully."}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    ## Upload a file
    # @param session_id: str
    # @param file: UploadFile
    # @return PythonResult
    def upload_file(
        self, 
        session_id: str, 
        session_manager: Dict[str, Any],
        file: UploadFile = File(...)
    ):
        try:
            # Create session directory if it doesn't exist
            session_dir = f"/tmp/{session_id}"
            os.makedirs(session_dir, exist_ok=True)

            file_location = f"{session_dir}/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

            session_manager[session_id]["files"].add(file_location)
            
            return {"filename": file.filename, "location": file_location}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))