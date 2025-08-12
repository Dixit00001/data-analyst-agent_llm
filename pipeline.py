from llm_utils import analyze_question, generate_code, review_and_debug_code
from executor import execute_code
import json

def run_pipeline(question_file: str, data_files: list):
    with open(question_file, "r") as f:
        question_text = f.read()

    steps = analyze_question(question_text)
    code = generate_code(steps, question_file, data_files)

    for _ in range(3):  # Retry up to 3 times
        output, error = execute_code(code, question_file, data_files)
        if error:
            code = review_and_debug_code(code, error)
            continue
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            code = review_and_debug_code(code, "Invalid JSON Output")
    return {"error": "Pipeline failed after retries"}
