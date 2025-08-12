import openai
from config import OPENAI_API_KEY, DEFAULT_MODEL

openai.api_key = OPENAI_API_KEY

def analyze_question(question_text: str) -> str:
    prompt = f"Break down the following data analysis task into precise steps:\n\n{question_text}"
    resp = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message["content"]

def generate_code(steps: str, question_file: str, data_files: list) -> str:
    files_list = "\n".join(data_files)
    prompt = f"""
Based on these analysis steps:

{steps}

Write Python code using Pandas, NumPy, and Matplotlib to:
1. Load input files:
   - Questions: {question_file}
   - Data: {files_list}

2. Perform the analysis and visualization.

3. Print the final result **only** as a JSON string.

No extra explanations or print statements.
"""
    resp = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message["content"]

def review_and_debug_code(code: str, error_message: str) -> str:
    prompt = f"""
Fix the following code.

CODE:
{code}

ERROR:
{error_message}

Return corrected code that performs the same task and outputs only JSON.
"""
    resp = openai.ChatCompletion.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message["content"]
