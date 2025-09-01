# Use the official Jupyter Notebook image
FROM jupyter/base-notebook:latest

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn python-multipart

# Copy the API script to the root directory
COPY api.py /home/jovyan/api.py
COPY README.md /home/jovyan/README.md

# Expose port 8888 for the Jupyter Notebook
EXPOSE 8888

# Expose an additional port for the FastAPI server
EXPOSE 8000