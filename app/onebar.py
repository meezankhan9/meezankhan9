"""Neuro Ninja Streamlit app."""
from __future__ import annotations

import streamlit as st

from utils.handles import detect_handles
from collectors import collect_all
from analysis.audit import generate_audit
from utils.io import save_raw, save_master, save_report


st.title("Neuro Ninja")

name = st.text_input("Candidate name")

with st.expander("Options"):
    months = st.number_input("Months", min_value=1, max_value=12, value=6)
    yt_key = st.text_input("YouTube API key", type="password")
    rivals = st.text_area("Rival handles (comma-separated)")
    sentiment = st.checkbox("Run sentiment sample", value=False)

if st.button("Search & Analyze") and name:
    handles = detect_handles(name)
    st.write("Detected handles:", handles)

    master = collect_all(handles, months, yt_key)
    if not master.empty:
        for platform, df in master.groupby("platform"):
            handle = handles.get(platform, "")
            save_raw(df, platform, handle)
        save_master(master)
        report = generate_audit(master, name)
        save_report(report, name)
        st.markdown(report)
        st.download_button(
            "Download report", report, file_name=f"{name}_audit.md"
        )
    else:
        st.warning("No data collected.")

# Placeholders for future integrations
# Facebook and WhatsApp collectors would be added here when official APIs are available.

