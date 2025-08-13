# Data Analyst Agent API (Hugging Face Version)

## Endpoints
- `/api/`: Upload CSV(s) + questions.txt → returns analytics and charts
- `/query`: JSON question → returns LLM-generated answer

## Setup
1. Install dependencies:
   pip install -r requirements.txt

2. Set environment variables before running:
   $env:HF_API_TOKEN="your_token_here"
   $env:NGROK_AUTHTOKEN="your_token_here"

3. Start FastAPI:
   uvicorn main:app --reload

4. Start ngrok in another terminal:
   ngrok http 8000

## Submission
- Submit **only** the base ngrok URL without any paths (`/docs`, `/api`, or `/query`)
- Keep FastAPI + ngrok running until evaluation ends.
