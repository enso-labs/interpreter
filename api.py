from fastapi import Body, Depends, FastAPI, HTTPException, File, Request, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi_mcp import FastApiMCP, AuthConfig
import subprocess
import os

from src.entities import *
from src.controllers import ExecController
from src.utils.session import get_session_id
from src.config import Config
from src.services.auth import authenticate_request
TAGS = ['MCP']
ID_NAME = "session_id"
MCP_OPERATIONS = [
    "install_packages",
    "code_execute",
    "terminate_session",
]



app = FastAPI(
    title=Config.TITLE,
    description=Config.DESCRIPTION,
    version=Config.VERSION,
    docs_url="/",
    # redoc_url="/redoc"
)
exec_controller = ExecController()
session_manager = {}

@app.post(
    "/install", 
    operation_id="install_packages",
    description="Install packages in isolated environment",
    tags=TAGS
)
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
                ID_NAME: session_id,
                **exec_controller.install_packages(session_id, session_manager, request.packages)
            }
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/execute", 
    operation_id="code_execute",
    description="Execute code in isolated environment",
    tags=TAGS,
    dependencies=[Depends(authenticate_request)]
)
def code_execute(body: CodeExecution = Body(...)):
    session_id = get_session_id(body)
    if session_id not in session_manager:
        session_manager[session_id] = {
            "packages": set(),
            "files": set()
        }
    
    try:
        # Write code to a temporary file
        code_file_path = exec_controller.exec_service.write_code(session_id, body.code)
        session_manager[session_id]["files"].add(code_file_path)

        return JSONResponse(
            status_code=200, 
            content={
                ID_NAME: session_id,
                **exec_controller.execute_python(code_file_path).model_dump()
            }
        )
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/terminate",
    operation_id="terminate_session",
    description="Terminate session",
    tags=TAGS
)
def terminate_session(request: SessionId):
    session_id = get_session_id(request)

    if session_id not in session_manager:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    try:
        deleted_session = exec_controller.exec_service.uninstall_packages(session_id, session_manager)
        return JSONResponse(
            status_code=200, 
            content={
                ID_NAME: session_id,
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
                ID_NAME: session_id,
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


mcp = FastApiMCP(
    app,
    name=Config.TITLE,
    description=Config.DESCRIPTION,
    include_operations=MCP_OPERATIONS,
    auth_config=AuthConfig(
        dependencies=[Depends(authenticate_request)],
    ),
    describe_all_responses=True,
    describe_full_response_schema=True,
)
mcp.mount()
mcp.setup_server()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
