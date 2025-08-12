import os
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from pipeline import run_pipeline
from pyngrok import ngrok
from config import NGROK_AUTHTOKEN

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")

@app.on_event("startup")
def startup_event():
    # Set token if provided in environment/config
    if NGROK_AUTHTOKEN:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
    # Start tunnel on port 8000
    public_url = ngrok.connect(8000)
    print(f"\n>>> Public ngrok URL: {public_url}\n")

@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),
    files: List[UploadFile] = []
):
    try:
        workdir = tempfile.mkdtemp()
        q_path = os.path.join(workdir, questions.filename)
        with open(q_path, "wb") as f:
            f.write(await questions.read())

        file_paths = []
        for file in files:
            fpath = os.path.join(workdir, file.filename)
            with open(fpath, "wb") as out:
                out.write(await file.read())
            file_paths.append(fpath)

        result = run_pipeline(q_path, file_paths)
        shutil.rmtree(workdir)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
