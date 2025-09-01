# Use the official Jupyter Notebook image
FROM jupyter/base-notebook:latest

# Copy the API script to the root directory
COPY mcp_wrap /home/jovyan/mcp_wrap
COPY src /home/jovyan/src
COPY api.py /home/jovyan/api.py
COPY requirements.txt /home/jovyan/requirements.txt

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# Expose port 8888 for the Jupyter Notebook
EXPOSE 8888

# Expose an additional port for the FastAPI server
EXPOSE 8000