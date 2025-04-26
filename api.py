from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
import uuid

from src.entities import *
from src.controllers import ExecController

app = FastAPI()
exec_controller = ExecController()
session_manager = {}


def get_session_id(request: SessionId):
    return request.session_id or str(uuid.uuid4())

@app.post("/install")
def install_packages(request: PackageInstall):
    session_id = get_session_id(request)
    
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        # Install packages if any are provided and not already installed
        return JSONResponse(
            status_code=200, 
            content={
                'id': session_id,
                **exec_controller.install_packages(session_id, session_manager, request.packages)
            }
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
def run_code(request: CodeExecution):
    session_id = get_session_id(request)
    
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        # Set environment variables
        for key, value in request.env.items():
            os.environ[key] = value

        # Write code to a temporary file
        code_file_path = exec_controller.exec_service.write_code(session_id, request.code)
        session_manager[session_id]["files"].add(code_file_path)

        return JSONResponse(
            status_code=200, 
            content={
                'id': session_id,
                **exec_controller.execute_python(code_file_path).model_dump()
            }
        )
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/terminate")
def terminate_session(request: SessionId):
    session_id = get_session_id(request)

    if session_id not in session_manager:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    try:
        deleted_session = exec_controller.exec_service.uninstall_packages(session_id, session_manager)
        return JSONResponse(
            status_code=200, 
            content={
                'id': session_id,
                **deleted_session
            }
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/upload")
async def create_upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        upload_file = exec_controller.upload_file(session_id, session_manager, file)
        return JSONResponse(
            status_code=200, 
            content={
                'id': session_id,
                **upload_file
            }
        )
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
    uvicorn.run(app, host="0.0.0.0", port=8020)
