import os
import sys
import ast
import re
import subprocess
import argparse
from huggingface_hub import InferenceClient

def get_token() -> str:
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Please set the HF_TOKEN environment variable.")
        sys.exit(1)
    return token

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--max_iter", type=int, default=5)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()

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

def get_error_type(traceback: str) -> str:
    lines = traceback.strip().split('\n')
    # The last line contains the error (e.g., "NameError: name 'x' is not defined")
    last_line = lines[-1]
    # Split by the colon to grab just the error type
    error_type = last_line.split(':')[0].strip()
    return error_type

def build_prompt(code: str, traceback: str, function_name: str) -> str:
    """Build prompt for debugging."""
    first_part = ""
    if traceback is None:
        first_part = f"""You are analyzing the following python code:
    {code}
    It produced no error. Fix logical error if any."""
    else:
        first_part = f"""You are debugging the following python code:
    {code}
    It produced the following error:
    {traceback}"""
    
    second_part = """ Do not return any other code, no explanation, and do not include markdown backticks.
Fix the root cause of the bug. Do not suppress errors with try/except unless exception handling is the correct fix.
DO NOT delete the previous code UNLESS it is wrong. """
    if function_name == "module":
        return first_part + "Return the corrected implementation of the entire python script." + second_part
    else:
        return first_part + f"Return ONLY the corrected implementation of function `{function_name}`. For import errors, use import inside function only." + second_part

def call_llm(client: InferenceClient, messages: list[dict[str, str]]) -> str:
    """Call LLM and return the response."""
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct:cheapest",
        messages=messages,
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
    
def react_loop(token: str, file_path: str, new_file_path: str, max_iter: int = 5, verbose: bool = False):
    client = InferenceClient(token=token)

    if (verbose):
        print("Agent: Running script...", end = " ")
    # Run the script once to get the initial traceback
    src_code, traceback = run_script(file_path)

    # Initialize messages for LLM conversation
    # messages order: system inst -> iteration log -> currentprompt 
    # This prompt structure is followed by modern ai labs like openai and anthropic.
    messages = []
    sys_prompt = "You are an Expert Python Developer and best at debugging python code. Return ONLY code as response."
    messages.append({"role":"system", "content": sys_prompt})
    for i in range(max_iter):
        # Get the function name from the traceback
        if traceback is not None:
            function_name = get_function_name_from_traceback(traceback)
            if verbose:
                if (function_name == 'module'):
                    print("Captured error at top level code")
                else:
                    print("Captured error in function", function_name)
        else:
            function_name = "module"
            if verbose:
                print("No runtime error found, checking for logical errors.")

        # Build the prompt for LLM
        prompt = build_prompt(src_code, traceback, function_name)
        if (verbose):
            print("Agent: Calling LLM with traceback + code context...")
        messages.append({"role":"user", "content": prompt})

        # Get the response from LLM
        response = call_llm(client, messages)
        if (verbose):
            print("LLM Response:\n", response)
            print("--- END OF RESPONSE ---")
        if (verbose):
            print("Agent: Applying fix via AST patch...")

        # Apply the fix to the code
        new_code = None
        if (function_name != "module"):
            new_ast = PythonSurgery(response).visit(ast.parse(src_code))
            new_code = ast.unparse(new_ast)
        else:
            new_code = response
        
        # Update conversation history
        debug_msg = (
            f"This is history of iteration: {i+1}\n"
            f"Error: {traceback}\n"
            f"Fix: {response}\n"
        )
        messages.append({"role":"assistant", "content": debug_msg})

        # Write patched file to disk
        if (verbose):
            print("Agent: Writing patched file to disk...")
        with open(new_file_path, 'w') as f:
            f.write(new_code)

        # Run the patched script to check for errors
        if (verbose):
            print("Agent: Running patched script...", end=" ")
        src_code, traceback = run_script(new_file_path)

        # If no traceback, bug is fixed
        if traceback is None:
            if (verbose):
                print(f"\nAgent: Fixed in {i+1} iterations. Patch saved to {new_file_path}")
            return {"sucess":True, "iterations":i+1}

    if (verbose):
        print(f"Agent: Failed to fix in {max_iter} iterations.")
    return {"sucess":False, "iterations":max_iter}

def main():
    args = parse_args()
    token = get_token()
    result = react_loop(token, args.script, args.script.replace('.py', '_fixed.py'), args.max_iter, args.verbose)

if __name__ == "__main__":
    main()