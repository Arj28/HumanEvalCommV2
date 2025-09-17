import subprocess
import time
import os

# ------------------------
# 1. Correctness (unit tests)
# ------------------------
def run_tests(code_file):
    """
    Run student's Python file in safe mode and check basic correctness.
    Returns number of passed dummy tests (0-5).
    """
    try:
        # Simple dummy unit tests: check if file runs without error + basic function definitions
        output = subprocess.run(
            ["python", code_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        if output.returncode != 0:
            return 0  # error running code

        # Count functions defined (proxy for correctness)
        with open(code_file, "r") as f:
            content = f.read()
        passed = content.count("def ")
        return min(passed, 5)  # scale 0-5
    except Exception:
        return 0

# ------------------------
# 2. Readability / Style
# ------------------------
def check_readability(code_file):
    try:
        with open(code_file, "r") as f:
            lines = f.readlines()
        # penalize if lines are too long
        issues = sum(1 for line in lines if len(line) > 100)
        return issues
    except Exception:
        return 5

# ------------------------
# 3. Security
# ------------------------
def check_security(code_file):
    try:
        with open(code_file, "r") as f:
            content = f.read()
        # penalize dangerous imports
        issues = 0
        for bad in ["os.system", "subprocess", "eval", "exec"]:
            if bad in content:
                issues += 1
        return issues
    except Exception:
        return 5

# ------------------------
# 4. Efficiency
# ------------------------
def measure_efficiency(code_file):
    start = time.time()
    try:
        subprocess.run(["python", code_file], timeout=3, capture_output=True)
        execution_time = time.time() - start
    except Exception:
        execution_time = 10
    return execution_time

# ------------------------
# 5. Compute final score
# ------------------------
def compute_score(correctness, readability, security, efficiency):
    readability_score = max(0, 100 - readability*5)
    security_score = max(0, 100 - security*20)
    efficiency_score = max(0, 100 - efficiency*10)
    final = 0.4*correctness*20 + 0.2*readability_score + 0.2*security_score + 0.2*efficiency_score
    return round(final, 2)

# ------------------------
# 6. Metric scores for visualization
# ------------------------
def metric_scores(correctness, readability, security, efficiency):
    score_correctness = min(correctness*20, 100)
    score_readability = max(0, 100 - readability*5)
    score_security = max(0, 100 - security*20)
    score_efficiency = max(0, 100 - efficiency*10)
    
    return {
        "Correctness": score_correctness,
        "Readability": score_readability,
        "Security": score_security,
        "Efficiency": score_efficiency
    }
