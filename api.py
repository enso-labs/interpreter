from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.responses import FileResponse
import subprocess
import os
import shutil
from typing import List, Dict

app = FastAPI(name="Enso Labs Interpreter", docs_url="/")

class CodeExecutionRequest(BaseModel):
    session_id: str
    code: str
    env: Dict[str, str] = {}

class PackageInstallationRequest(BaseModel):
    session_id: str
    packages: List[str]

class TerminateSessionRequest(BaseModel):
    session_id: str

session_manager = {}

@app.post("/install")
def install_packages(request: PackageInstallationRequest):
    session_id = request.session_id
    
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        # Install packages if any are provided and not already installed
        for package in request.packages:
            if package not in session_manager[session_id]["packages"]:
                subprocess.check_call([f"pip install {package}"], shell=True)
                session_manager[session_id]["packages"].add(package)
        
        return {"status": "success", "installed_packages": list(session_manager[session_id]["packages"])}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
def run_code(request: CodeExecutionRequest):
    session_id = request.session_id
    
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        # Set environment variables
        for key, value in request.env.items():
            os.environ[key] = value

        # Create session directory if it doesn't exist
        session_dir = f"/tmp/{session_id}"
        os.makedirs(session_dir, exist_ok=True)

        # Write code to a temporary file
        code_file_path = f"{session_dir}/temp_code.py"
        with open(code_file_path, "w") as code_file:
            code_file.write(request.code)
        session_manager[session_id]["files"].add(code_file_path)

        # Run the code
        result = subprocess.run(["python", code_file_path], capture_output=True, text=True)

        return {"status": "success", "output": result.stdout, "errors": result.stderr}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def create_upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
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

@app.post("/terminate")
def terminate_session(request: TerminateSessionRequest):
    session_id = request.session_id

    if session_id not in session_manager:
        raise HTTPException(status_code=404, detail="Session not found.")
    
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
    
@app.get("/download")
def download_file(session_id: str, filename: str):
    session_dir = f"/tmp/{session_id}"
    file_path = f"{session_dir}/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(path=file_path, filename=filename)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8100)))
