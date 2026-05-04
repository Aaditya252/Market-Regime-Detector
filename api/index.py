"""FastAPI wrapper to run Streamlit on Vercel"""
import subprocess
import threading
import time
from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Flag to track if Streamlit server is running
streamlit_running = False

def start_streamlit():
    """Start Streamlit server in background"""
    global streamlit_running
    if not streamlit_running:
        subprocess.Popen([
            "streamlit",
            "run",
            "app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--logger.level=error",
        ], cwd="/tmp")
        streamlit_running = True
        time.sleep(2)  # Wait for server to start

@app.get("/")
async def root():
    """Redirect to Streamlit app"""
    start_streamlit()
    return {"message": "Streamlit app running at http://localhost:8501"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
