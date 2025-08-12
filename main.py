from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from typing import Optional, List
import tempfile
import shutil
import os
from pipeline import run_pipeline
import openai
import json

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")

# ---- 1. Root + Health ----
@app.get("/")
async def root():
    return {"message": "Welcome to the LLM-Powered Data Analyst API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ---- 2. Data Analyst Agent Endpoint ----
@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),
    files: Optional[List[UploadFile]] = File(None)
):
    try:
        workdir = tempfile.mkdtemp()

        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No CSV file provided")

        # Save first CSV
        csv_path = os.path.join(workdir, files[0].filename)
        with open(csv_path, "wb") as f:
            f.write(await files[0].read())

        # Run analysis
        result = run_pipeline(questions.file, [csv_path])

        shutil.rmtree(workdir)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- 3. IITM Checker Endpoint ----
@app.post("/query")
async def query_endpoint(request: Request):
    """
    IITM auto-checker will call this.
    Expects JSON with a key: "question"
    Returns JSON with exactly one key: "answer"
    """
    try:
        data = await request.json()
        question = data.get("question", "").strip()

        if not question:
            return {"answer": "No question provided."}

        # Call OpenAI with approved model
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o",  # ✅ CHANGED from openai/gpt-4.1
            messages=[{"role": "user", "content": question}],
            temperature=0
        )

        answer = completion.choices[0].message.content.strip()
        return {"answer": answer}

    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
