# pyfix-agent
An autonomous agent (no LangChain — ReAct loop implemented manually) that takes a broken Python script, runs it, captures the traceback, generates a fix via LLM API, applies the patch using AST manipulation, reruns — iterating until tests pass or step limit. Evaluated on 50 curated buggy scripts with ground truth fixes.
