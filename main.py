from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
import tempfile
import shutil
import os
from pipeline import run_pipeline
from pyngrok import ngrok
from config import NGROK_AUTHTOKEN

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")

@app.on_event("startup")
def startup_event():
    if NGROK_AUTHTOKEN:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
    public_url = ngrok.connect(8000)
    print(f"\n>>> Public ngrok URL: {public_url}\n")

@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),  # Required
    files: Optional[List[UploadFile]] = File(None)  # Now truly optional
):
    try:
        # Create temp workdir
        workdir = tempfile.mkdtemp()

        # Save questions.txt
        q_path = os.path.join(workdir, questions.filename)
        with open(q_path, "wb") as f:
            f.write(await questions.read())

        # Save files if any are uploaded
        file_paths = []
        if files:
            for file in files:
                if file:  # Avoids None entries
                    fpath = os.path.join(workdir, file.filename)
                    with open(fpath, "wb") as out:
                        out.write(await file.read())
                    file_paths.append(fpath)

        # Run your pipeline
        result = run_pipeline(q_path, file_paths)

        # Clean up
        shutil.rmtree(workdir)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

