import subprocess
import sys

def run_script(file_path: str) -> tuple[str, str | None]:
    """ Runs the given Python script and returns source_code and traceback if any. """
    with open(file_path, 'r') as f:
        src_code = f.read()
    result = subprocess.run([sys.executable, file_path], text=True, capture_output=True)
    traceback = None
    if result.returncode != 0:
        traceback = result.stderr
    return src_code, traceback

def build_prompt(code: str, traceback: str) -> str:
    """Build prompt for debugging."""

    return f"""You are debugging Python code. Here is the code:
{code}
It produced this error:
{traceback}
Return ONLY the corrected full function/script, no explanation."""

def main():
    file_path = "script.py"
    src_code, traceback = run_script(file_path)
    prompt = build_prompt(src_code, traceback)
    print(prompt)

if __name__ == "__main__":
    main()