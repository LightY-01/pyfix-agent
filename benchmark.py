import os
import csv
import sys
import subprocess
import time
from pyfix_agent import react_loop, get_token
from huggingface_hub.utils import HfHubHTTPError

token = get_token()

with open("benchmark_results.csv", "a", newline="") as csvfile:
    writer = csv.writer(csvfile)

    categories = ["NameError", "IndexError", "TypeError", "AttributeError", "LogicBugs"]
    for category in categories:
        print(f"Fixing scripts in {category} category...")
        for i in range(1,4):
            while True:
                try:
                    print(f"Fixing script{i}.py...", end=" ")
                    result = react_loop(token, f"eval_dataset/{category}/script{i}.py", f"eval_dataset/{category}/patched_script{i}.py")
                    status = "Failed"
                    try:
                        subprocess.run([sys.executable, f"eval_dataset/{category}/test_script{i}.py"], check=True)
                        status = "Fixed"
                    except Exception as e:
                        pass
                    writer.writerow([f"{category}/script{i}.py", status, result["iterations"]])
                    print(f"Finished script{i}.py")
                    time.sleep(30)
                    break
                except HfHubHTTPError as e:
                    if e.response.status_code == 402:
                        print("Hit the 402 micro-window ceiling. Waiting 90 seconds to reset ...")
                        time.sleep(90)
                    else:
                        raise e

print("\nDone")
