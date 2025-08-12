from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Optional, List
import tempfile
import shutil
import os
from pipeline import run_pipeline

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM-Powered Data Analyst API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),  # required
    files: Optional[List[UploadFile]] = File(None)  # optional
):
    try:
        workdir = tempfile.mkdtemp()

        # Validation: must have at least 1 CSV file
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No CSV file provided")

        # Save CSV locally
        csv_path = os.path.join(workdir, files[0].filename)
        with open(csv_path, "wb") as f:
            f.write(await files[0].read())

        # Run pipeline and return results
        result = run_pipeline(questions.file, [csv_path])

        shutil.rmtree(workdir)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

