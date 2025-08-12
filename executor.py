import subprocess
import tempfile
import os

def execute_code(code: str, question_file: str, data_files: list):
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, "analysis.py")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        process = subprocess.run(
            ["python", script_path],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=100
        )
        if process.returncode != 0:
            return None, process.stderr
        return process.stdout.strip(), None
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"

