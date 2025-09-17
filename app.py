import streamlit as st
import tempfile
import os
import csv
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="HumanEvalComm V2", layout="wide")
st.title("HumanEvalComm V2 - Multi-file Support")

# Colors
bg_color = "#FFFFFF"
text_color = "#000000"
bar_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2 = st.tabs(["Code Evaluation", "Leaderboard"])

# -----------------------------
# Predefined unit tests (example)
# -----------------------------
PREDEFINED_TESTS = {
    "add": [((2, 3), 5), ((-1, 1), 0)],
    "multiply": [((2, 3), 6), ((-1, 5), -5)],
}

# -----------------------------
# Helper Functions
# -----------------------------
def run_tests(code_file):
    try:
        namespace = {}
        with open(code_file, "r") as f:
            exec(f.read(), namespace)
        passed_count = 0
        total_tests = 0
        for func_name, tests in PREDEFINED_TESTS.items():
            func = namespace.get(func_name)
            if callable(func):
                for args, expected in tests:
                    total_tests += 1
                    try:
                        if func(*args) == expected:
                            passed_count += 1
                    except:
                        pass
        if total_tests == 0:
            return 0
        score = min(5, round(5 * (passed_count / total_tests)))
        return score
    except:
        return 0

def check_readability(code_file):
    try:
        with open(code_file, "r") as f:
            lines = f.readlines()
        issues = sum(1 for line in lines if len(line) > 100)
        return issues
    except:
        return 5

def check_security(code_file):
    try:
        with open(code_file, "r") as f:
            content = f.read()
        issues = sum(1 for bad in ["os.system", "subprocess", "eval", "exec"] if bad in content)
        return issues
    except:
        return 5

def measure_efficiency(code_file):
    start = time.time()
    try:
        os.system(f"python {code_file}")
        exec_time = time.time() - start
    except:
        exec_time = 10
    return exec_time

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

def compute_score(correctness, readability, security, efficiency):
    scores = metric_scores(correctness, readability, security, efficiency)
    final = 0.4*scores["Correctness"] + 0.2*scores["Readability"] + 0.2*scores["Security"] + 0.2*scores["Efficiency"]
    return round(final, 2)

# -----------------------------
# TAB 1: CODE EVALUATION
# -----------------------------
with tab1:
    name = st.text_input("Your Name:")
    st.markdown("### ✍️ Write or Upload Your Code")
    code_input = st.text_area("Write your Python code here:", height=250, placeholder="def add(a, b):\n    return a + b")
    uploaded_file = st.file_uploader("Or upload a Python file (.py)", type=["py"])

    if uploaded_file:
        try:
            code_input = uploaded_file.read().decode("utf-8", errors="ignore")
            file_name = uploaded_file.name
        except:
            code_input = ""
            file_name = "uploaded_file.py"
    else:
        file_name = "written_code.py"

    if st.button("Evaluate"):
        if not name or not code_input.strip():
            st.error("Enter your name and either write or upload code!")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
                tmp.write(code_input.encode("utf-8"))
                tmp_path = tmp.name

            correctness = run_tests(tmp_path)
            readability = check_readability(tmp_path)
            security = check_security(tmp_path)
            efficiency = measure_efficiency(tmp_path)
            scores = metric_scores(correctness, readability, security, efficiency)
            final_score = compute_score(correctness, readability, security, efficiency)

            # Display chart
            score_df = pd.DataFrame(list(scores.items()), columns=["Metric", "Score"])
            fig = px.bar(score_df, x="Metric", y="Score", color="Score", text="Score", range_y=[0,100], color_continuous_scale=bar_colors, title="Metric Scores")
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"🏆 Python Final Score: {final_score}/100")
            st.subheader("📋 Your Code")
            st.text_area("Your Python Code", value=code_input, height=300)

            # Save to leaderboard
            lb_file = "leaderboard.csv"
            if not os.path.exists(lb_file):
                with open(lb_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "File", "Score", "Content", "Timestamp"])
            with open(lb_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([name, file_name, final_score, code_input, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# -----------------------------
# TAB 2: LEADERBOARD
# -----------------------------
with tab2:
    st.subheader("🏆 Leaderboard")
    lb_file = "leaderboard.csv"
    if os.path.exists(lb_file):
        lb = pd.read_csv(lb_file)
        last_updated = lb["Timestamp"].max()
        st.caption(f"⏰ Last Updated: {last_updated}")
        search_name = st.text_input("🔍 Search by Name")
        sort_option = st.selectbox("Sort Leaderboard By:", ["Score (High → Low)", "Score (Low → High)", "Date (Newest First)", "Date (Oldest First)"])
        if sort_option == "Score (High → Low)":
            lb = lb.sort_values(by="Score", ascending=False)
        elif sort_option == "Score (Low → High)":
            lb = lb.sort_values(by="Score", ascending=True)
        elif sort_option == "Date (Newest First)":
            lb = lb.sort_values(by="Timestamp", ascending=False)
        else:
            lb = lb.sort_values(by="Timestamp", ascending=True)
        if search_name:
            lb = lb[lb["Name"].str.contains(search_name, case=False, na=False)]
        lb_top10 = lb.head(10).reset_index(drop=True)
        for i, row in lb_top10.iterrows():
            with st.expander(f"{i+1}. {row['Name']} - File: {row['File']} - Score: {row['Score']}"):
                st.text_area("Submitted Code", value=row['Content'], height=200, key=f"code_{i}")
        st.markdown("### 📊 Quick Scores Table")
        st.table(lb_top10[["Name","File","Score","Timestamp"]])
        csv_data = lb_top10[["Name","File","Score","Timestamp"]].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Leaderboard (CSV)", data=csv_data, file_name="leaderboard_top10.csv", mime="text/csv")
    else:
        st.info("Leaderboard is empty. Be the first to submit!")

# -----------------------------
# Custom Styles
# -----------------------------
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)
