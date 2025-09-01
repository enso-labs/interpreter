import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    API_URL = os.getenv("API_URL", "http://localhost:8020")
    VERSION = os.getenv("VERSION", "0.1.0")
    TITLE = os.getenv("TITLE", "MCP Python Sandbox")
    DESCRIPTION = os.getenv("DESCRIPTION", "MCP API for Python Sandbox by Ensō Labs")
