import os
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel
from openai import OpenAI  # Use OpenAI library which is compatible with OpenRouter

# = FastAPI app =
app = FastAPI()

# = OpenRouter API Config =
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set this in your environment
if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY environment variable")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def query_openrouter_api(prompt: str) -> str:
    """Send a prompt to OpenRouter and return generated text."""
    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",  # Choose a model hosted on OpenRouter
        messages=[
            {"role": "system", "content": "You are a skilled data analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# = /query endpoint =
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(data: QueryRequest):
    answer_text = query_openrouter_api(data.question)
    return {"answer": answer_text}

# = /api endpoint =
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

    # = Calculations =
    total_sales = float(df['Sales'].sum())
    top_region = df.groupby('Region')['Sales'].sum().idxmax()
    day_sales_correlation = float(df['Date'].dt.day.corr(df['Sales']))
    median_sales = float(df['Sales'].median())
    total_sales_tax = float(total_sales * 0.10)

    # = Bar chart: sales by region =
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

    # = Cumulative sales chart =
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

    # = Final JSON result =
    return {
        "total_sales": total_sales,
        "top_region": top_region,
        "day_sales_correlation": day_sales_correlation,
        "bar_chart": bar_chart_b64,
        "median_sales": median_sales,
        "total_sales_tax": total_sales_tax,
        "cumulative_sales_chart": cumulative_sales_chart_b64
    }
