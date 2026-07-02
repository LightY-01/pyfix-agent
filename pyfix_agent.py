import os
import sys
import ast
import re
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

def get_function_name_from_traceback(traceback: str) -> str | None:
    # Use regex to find the last occurrence of in <function_name>
    matches = re.findall(r'in (\w+|<module>)', traceback)
    if matches:
        return matches[-1].replace("<", "").replace(">", "")
    return None

def build_prompt(code: str, traceback: str, function_name: str) -> str:
    """Build prompt for debugging."""

    return f"""You are an Expert Python Developer. You are debugging the following python code:
{code}
It produced the following error:
{traceback}
Return ONLY the corrected implementation of function `{function_name}`.
Do not return any other code, no explanation, and do not include markdown backticks."""

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

class PythonSurgery(ast.NodeTransformer):
    def __init__(self, new_code: str):
        self.new_node = ast.parse(new_code).body[0]

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.new_node.name:
            ast.copy_location(self.new_node, node)
            return self.new_node
        return node
    
def react_loop(file_path: str, new_file_path: str, max_iter: int = 5):
    src_code, traceback = run_script(file_path)
    print(traceback)
    for i in range(max_iter):
        function_name = get_function_name_from_traceback(traceback)

        prompt = build_prompt(src_code, traceback, function_name)
        response = call_llm(prompt)
        print("Response:\n", response)
        
        new_code = None
        if (function_name != "module"):
            new_ast = PythonSurgery(response).visit(ast.parse(src_code))
            new_code = ast.unparse(new_ast)
        else:
            new_code = response
            
        print("Patched Code:\n", new_code)

        with open(new_file_path, 'w') as f:
            f.write(new_code)

        src_code, traceback = run_script(new_file_path)
        if traceback is None:
            print("Script fixed successfully!")
            break

def main():
    file_path = "script.py"
    new_file_path = "script_fixed.py"
    react_loop(file_path, new_file_path)

if __name__ == "__main__":
    main()