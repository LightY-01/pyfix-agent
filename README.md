# PyFix Agent: Autonomous ReAct Debugging Loop

An autonomous, multi-turn AI debugging agent built entirely from scratch in Python. 

Unlike standard wrappers that simply ask an LLM to "fix this code," **PyFix Agent** implements a custom **ReAct (Reasoning and Acting)** state machine and utilizes **Abstract Syntax Tree (AST)** manipulation to surgically patch Python files in real-time. It evaluates its own fixes by executing the code inside a sandboxed subprocess, iterating dynamically until the script passes or it reaches the maximum iteration limit.

---

## Core Architecture

This project deliberately avoids high-level agentic abstractions (such as LangChain or LlamaIndex) to build the core agentic loop from first principles.

1. **Execution Engine**: Runs the target script via Python subprocesses, capturing standard outputs, standard errors, and stack traces with safety timeout thresholds.
2. **Context Memory**: Maintains a chronological conversation history array, allowing the LLM to learn from its previously failed patching attempts without losing the original code context.
3. **AST Surgery**: Parses the LLM's response and uses Python's native `ast.NodeTransformer` to swap out broken function nodes with the corrected logic, leaving the rest of the file entirely untouched.

---

## Design Choices & Trade-offs

Building an autonomous agent requires balancing safety, context window limits, and real-world unpredictability.

### 1. AST Function Surgery vs. Full File Overwrites
* **The Problem**: Asking an LLM to rewrite an entire 1,000-line script to fix a single typo is slow, expensive, and risks the model "truncating" or getting lazy with existing, working code.
* **The Solution**: The agent extracts the specific `function_name` from the traceback. It prompts the LLM only for the corrected function. The `PythonSurgery` class (inheriting from `ast.NodeTransformer`) then traverses the syntax tree, finds the broken `ast.FunctionDef`, and seamlessly swaps it with the new node.
* **The Trade-off**: While this guarantees perfect preservation of unrelated code, it requires specialized routing logic for errors that occur at the top-level `<module>` scope, which bypass the AST function surgery and require full-file patching.

### 2. Execution-Based Evaluation vs. Exact String Matching
* **The Problem**: How do we benchmark if the agent successfully fixed a bug? Traditional exact string matching fails because the LLM might use different variable names (e.g., `x += 1` instead of `x = x + 1`), resulting in false negatives.
* **The Solution**: The evaluation suite uses **Execution-Based Benchmarking**. The benchmark dynamically runs automated unit tests or validation scripts containing assertion statements against the patched files. If the patched script exits with code 0, it is marked as a success.

---

## Evaluation Benchmark

The agent is evaluated against a curated dataset of scripts spanning 5 distinct error categories:
* **NameError**: Undefined variables, scope issues, and missing imports.
* **IndexError**: Off-by-one loop conditions and bounds checking.
* **TypeError**: Data type mismatches and unsupported operations.
* **AttributeError**: Typographical errors in object methods or calling methods on `NoneType`.
* **Logic Bugs**: Silent errors that require execution-based assertions to detect.

*(Currently evaluated against an automated function-level testing benchmark suite inside `eval_dataset/`)*

---

## Installation & Usage

### Install via pip (Recommended)

You can install PyFix Agent directly from PyPI:

```bash
pip install pyfix-agent
```

This will automatically register the `pyfix-agent` executable in your terminal path.

### Install from Source

If you want to run or modify the source code locally:

```bash
# Clone the repository
git clone https://github.com/LightY-01/pyfix-agent.git
cd pyfix-agent

# Install package in editable mode
pip install -e .
```

### Configuration

Export your Hugging Face Hub token to your environment variables to ensure secure API access:

**Bash (Linux/macOS):**
```bash
export HF_TOKEN="your_huggingface_token_here"
```

**PowerShell (Windows):**
```powershell
$env:HF_TOKEN="your_huggingface_token_here"
```

---

## CLI Usage Guide

Point the agent at any broken Python script. Use the `--verbose` flag to watch the ReAct state machine's internal thought process.

```bash
# Run the agent CLI
pyfix-agent --script buggy_script.py --verbose --max_iter 5
```

### CLI Command Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `--script` | `str` | *Required* | Path to the broken Python script to debug |
| `--max_iter` | `int` | `5` | Maximum number of debugging iterations |
| `--verbose` | `flag` | `False` | Enable logging of reasoning, tracebacks, and raw LLM responses |

### Running the Evaluation Benchmark

To run the full evaluation suite against the benchmark:

```bash
python benchmark.py
```

