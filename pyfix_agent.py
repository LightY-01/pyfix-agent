import os
import sys
import subprocess
from huggingface_hub import InferenceClient

token = os.environ.get("HF_TOKEN")
if not token:
    print("Please set the HF_TOKEN environment variable.")
    sys.exit(1)

client = InferenceClient(token=token)

def run_script(file_path: str) -> tuple[str, str | None]:
    """ Runs the given Python script and returns source_code and traceback if any. """
    with open(file_path, 'r') as f:
        src_code = f.read()
    result = subprocess.run(
        [sys.executable, file_path], 
        text=True, 
        capture_output=True,
        timeout=10
    )
    traceback = None
    if result.returncode != 0:
        traceback = result.stderr
    return src_code, traceback

def build_prompt(code: str, traceback: str) -> str:
    """Build prompt for debugging."""

    return f"""You are an Expert Python Developer. You are debugging the following python code:
{code}
It produced the following error:
{traceback}
Return ONLY the corrected full python code, no explanation."""

def call_llm(prompt: str) -> str:
    """Call LLM and return the response."""
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content
    

def main():
    file_path = "script.py"
    src_code, traceback = run_script(file_path)
    prompt = build_prompt(src_code, traceback)
    response = call_llm(prompt)
    print(response)

if __name__ == "__main__":
    main()