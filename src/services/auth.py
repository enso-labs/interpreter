
from fastapi import Request
import os

def authenticate_request(request: Request):
     # Set environment variables from request headers with EXEC_ prefix
    for key, value in request.headers.items():
        if key.lower().startswith("exec_"):
            env_var = key.upper().replace("EXEC_", "")
            os.environ[env_var] = value
    return request