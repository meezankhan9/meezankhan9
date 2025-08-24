"""Neuro Ninja one-bar Streamlit app."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

st.title("Neuro Ninja")

name = st.text_input("Candidate name")
with st.expander("Options (optional)"):
    months = st.slider("Months", 1, 18, 12)
    yt_key = st.text_input("YouTube API key", type="password")
    rivals = st.text_input("Competitors (platform:handle, comma separated)")
    sentiment = st.checkbox("Include sentiment sample", value=False)

log_expander = st.expander("Logs")

if st.button("Search & Analyze") and name:
    cmd = [
        sys.executable,
        "-m",
        "src.pipeline.run_audit",
        "--name",
        name,
        "--months",
        str(months),
    ]
    if yt_key:
        cmd += ["--youtube-key", yt_key]
    if rivals:
        cmd += ["--rivals", rivals]
    if sentiment:
        cmd.append("--sentiment")

    with st.spinner("Collecting and analyzing data..."):
        proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.stderr:
        log_expander.code(proc.stderr)
    if proc.returncode != 0:
        st.error("Audit failed")
    else:
        try:
            result = json.loads(proc.stdout.strip() or "{}")
        except json.JSONDecodeError:
            st.error("Invalid response from auditor")
            log_expander.code(proc.stdout)
        else:
            st.write("Detected handles:", result.get("handles", {}))
            summary_md = result.get("summary_md", "")
            st.markdown(summary_md)
            report_path = result.get("report_path")
            if report_path and Path(report_path).exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "Download report (.md)",
                        f.read(),
                        file_name=Path(report_path).name,
                    )
            else:
                st.warning("Report file missing")
