from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from typing import Optional, List
import tempfile
import shutil
import os
from pipeline import run_pipeline
import openai

app = FastAPI(title="LLM-Powered Data Analyst Agent with ngrok")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the LLM-Powered Data Analyst API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Data Analyst API endpoint
@app.post("/api/")
async def api_endpoint(
    questions: UploadFile = File(...),
    files: Optional[List[UploadFile]] = File(None)
):
    try:
        workdir = tempfile.mkdtemp()

        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No CSV file provided")

        csv_path = os.path.join(workdir, files[0].filename)
        with open(csv_path, "wb") as f:
            f.write(await files[0].read())

        result = run_pipeline(questions.file, [csv_path])

        shutil.rmtree(workdir)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# IITM checker expected /query endpoint
@app.post("/query")
async def query_endpoint(request: Request):
    """
    Expects JSON with a 'question' key.
    Returns JSON with 'answer' key containing response string.
    """
    try:
        data = await request.json()
        question = data.get("question", "").strip()
        if not question:
            return {"answer": "No question provided."}

        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question}],
            temperature=0
        )
        answer = completion.choices[0].message.content.strip()
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

