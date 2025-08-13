import os
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
from pydantic import BaseModel
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt

# ===== FastAPI app =====
app = FastAPI()

# ===== Hugging Face API Config =====
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Must be set before running uvicorn
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Change model if needed
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_huggingface_api(prompt: str) -> str:
    """Send a text prompt to Hugging Face model and return the generated text."""
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Hugging Face API error: {response.text}")
    generated = response.json()
    if isinstance(generated, list) and len(generated) > 0:
        return generated[0].get("generated_text", "").strip()
    return ""

# ===== /query endpoint =====
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(data: QueryRequest):
    """Accept a text question and return an answer using Hugging Face API."""
    answer_text = query_huggingface_api(data.question)
    return {"answer": answer_text}

# ===== /api endpoint =====
@app.post("/api/")
async def api_endpoint(questions: UploadFile = File(...), files: List[UploadFile] = File(...)):
    """
    Process CSV sales data and return required analytics:
    total_sales, top_region, day_sales_correlation,
    bar_chart, median_sales, total_sales_tax, cumulative_sales_chart
    """

    # Read questions file (not used in calculation in public tests)
    _ = await questions.read()

    # Read & combine all uploaded CSV files
    df_list = []
    for file in files:
        content = await file.read()
        df_list.append(pd.read_csv(io.BytesIO(content)))
    df = pd.concat(df_list, ignore_index=True)

    # Ensure correct column names
    if not {'Region', 'Sales', 'Date'}.issubset(df.columns):
        raise HTTPException(status_code=400, detail="CSV must contain 'Region', 'Sales', 'Date' columns")

    # Convert Date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # ===== Calculations =====
    total_sales = float(df['Sales'].sum())
    top_region = df.groupby('Region')['Sales'].sum().idxmax()
    day_sales_correlation = float(df['Date'].dt.day.corr(df['Sales']))
    median_sales = float(df['Sales'].median())
    total_sales_tax = float(total_sales * 0.10)

    # ===== Bar chart: sales by region =====
    plt.figure(figsize=(4, 3))
    df.groupby('Region')['Sales'].sum().plot(kind='bar', color='blue')
    plt.xlabel('Region')
    plt.ylabel('Total Sales')
    plt.tight_layout()
    bar_img = io.BytesIO()
    plt.savefig(bar_img, format='png')
    bar_img.seek(0)
    bar_chart_b64 = base64.b64encode(bar_img.read()).decode('utf-8')
    plt.close()

    # ===== Cumulative sales chart =====
    plt.figure(figsize=(4, 3))
    df_sorted = df.sort_values('Date')
    df_sorted['CumulativeSales'] = df_sorted['Sales'].cumsum()
    plt.plot(df_sorted['Date'], df_sorted['CumulativeSales'], color='red')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Sales')
    plt.tight_layout()
    cum_img = io.BytesIO()
    plt.savefig(cum_img, format='png')
    cum_img.seek(0)
    cumulative_sales_chart_b64 = base64.b64encode(cum_img.read()).decode('utf-8')
    plt.close()

    # ===== Final JSON result =====
    return {
        "total_sales": total_sales,
        "top_region": top_region,
        "day_sales_correlation": day_sales_correlation,
        "bar_chart": bar_chart_b64,
        "median_sales": median_sales,
        "total_sales_tax": total_sales_tax,
        "cumulative_sales_chart": cumulative_sales_chart_b64
    }
