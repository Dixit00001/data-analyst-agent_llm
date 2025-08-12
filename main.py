from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
import tempfile
import shutil
import os
from pipeline import run_pipeline
from pyngrok import ngrok
from config import NGROK_AUTHTOKEN

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")


# ✅ Simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup_event():
    """Start ngrok tunnel at app startup."""
    if NGROK_AUTHTOKEN:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
    # Explicitly bind to the local IP and port
    public_url = ngrok.connect("127.0.0.1:8000")
    print(f"\n>>> Public ngrok URL: {public_url}\n")

@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),  # Required
    files: Optional[List[UploadFile]] = File(None)  # Truly optional
):
    try:
        # Create temporary working directory
        workdir = tempfile.mkdtemp()

        # Save questions file
        q_path = os.path.join(workdir, questions.filename)
        with open(q_path, "wb") as f:
            f.write(await questions.read())

        # Save extra data files if provided
        file_paths = []
        if files:
            for file in files:
                if file:  # skip None entries
                    fpath = os.path.join(workdir, file.filename)
                    with open(fpath, "wb") as out:
                        out.write(await file.read())
                    file_paths.append(fpath)

        # Run your data analysis pipeline
        result = run_pipeline(q_path, file_paths)

        # Clean up temp folder
        shutil.rmtree(workdir)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
