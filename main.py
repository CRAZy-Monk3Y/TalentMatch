# --- main.py ---
import json
import sqlite3
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from agents.jd_summarizer import summarize_jd
from agents.recruiter import process_resumes
from agents.scheduler import generate_emails
from agents.shortlister import shortlist_candidates
from utils.pdf_reader import extract_text_from_pdf

# Connect to SQLite DB
conn = sqlite3.connect("db/job_screening.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    job_title TEXT,
    candidate_name TEXT,
    candidate_email TEXT,
    candidate_resume TEXT,
    match_score INTEGER,
    summary TEXT, 
    screening_date TEXT
)
""")
conn.commit()


st.set_page_config(page_title=" TalentMatch", layout="wide",page_icon="logo.png")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    </style>
""",
    unsafe_allow_html=True,
)
col1,col2=st.columns([1,9])
with col1:
    st.image("logo.png")
with col2:
    st.title("TatlentMatch", anchor=False)

# Upload JD
jd_file = st.file_uploader(
    "Upload Job Description CSV (with columns 'Job Title' and 'Job Description')",
    type=["csv"],
    accept_multiple_files=False,
    help="Upload a CSV file containing job titles and their descriptions. Each row should represent a distinct job role.",
)
threshold = st.slider(
    "Set Matching Threshold %",
    50,
    100,
    80,
    5,
    help="Set the minimum match score required for a candidate to be shortlisted.",
)
resume_files = st.file_uploader(
    "Upload Candidate Resumes (PDF)",
    type="pdf",
    accept_multiple_files=True,
    help="Upload one or more candidate resumes in PDF format to evaluate against the job descriptions.",
)

if st.button(
    "Run Screening",
    disabled=not jd_file or not resume_files,
    help="Run the screening pipeline using the uploaded job descriptions and candidate resumes.",
):
    screening_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
    if jd_file and resume_files:
        progress_val = 0
        progress_bar = st.progress(progress_val, "Starting the Screening...")
        jd_df = pd.read_csv(
            jd_file, usecols=["Job Title", "Job Description"], encoding="ISO-8859-1"
        )
        jd_df.dropna(axis=0, inplace=True)
        progress_segments = int(100 / (jd_df.shape[0] * 4))
        # st.write(progress_segments)
        if "Job Title" in jd_df.columns and "Job Description" in jd_df.columns:
            all_shortlisted = []
            all_emails = {}
            all_resumes = []
            shortlisted_resumes = []
            for files in resume_files:
                resume = extract_text_from_pdf(files)
                all_resumes.append(resume)
            for index, row in jd_df.iterrows():
                jd_summary = summarize_jd(row["Job Title"], row["Job Description"])
                progress_val += progress_segments
                progress_bar.progress(
                    progress_val,
                    f"Overall completion {progress_val}% Summarized JD: {json.loads(jd_summary)['title']}",
                )
                # st.write("JD Summary:", jd_summary)
                candidates = process_resumes(
                    all_resumes,
                    jd_summary,
                    progress_bar,
                    progress_val,
                    progress_segments,
                )
                # st.write("Candidates: ", candidates)
                shortlisted = shortlist_candidates(
                    candidates,
                    all_resumes,
                    threshold,
                    progress_bar,
                    progress_val,
                    progress_segments,
                    shortlisted_resumes,
                )
                if len(shortlisted) == 0:
                    st.warning(
                        f"No Suitable candidates found for the role {json.loads(jd_summary)['title']}"
                    )
                    progress_val += progress_segments * 2
                    continue
                # st.write("Shortlisted Candidates",shortlisted)
                # progress_val += progress_segments
                # progress_bar.progress(
                #     progress_val,
                #     f"Overall completion {progress_val}% Shortlisted Candidates for: {json.loads(jd_summary)['title']}",
                # )
                emails = generate_emails(
                    shortlisted,
                    jd_summary,
                    progress_bar,
                    progress_val,
                    progress_segments,
                )
                # st.write("Emails", emails)

                for candidate in shortlisted:
                    candidate["jd_summary"] = jd_summary
                all_shortlisted.extend(shortlisted)
                all_emails.update(emails)

                # Save to DB
                for index, c in enumerate(shortlisted):
                    cursor.execute(
                        "INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            row["Job Title"],
                            c["name"],
                            c["email"],
                            shortlisted_resumes[index],
                            c["match"],
                            str(jd_summary),
                            screening_time,
                        ),
                    )
                conn.commit()
            with st.container(border=True):
                st.subheader("Results", anchor=False)
                for c in all_shortlisted:
                    with st.expander(
                        f"**{c['name']}** - Match: {c['match']}% for JD: **{json.loads(c['jd_summary'])['title']}**"
                    ):
                        # st.write(c)
                        # st.markdown(f"**{c['name']}** - Match: {c['match']}%")
                        st.code(
                            all_emails[c["email"]], language="text", wrap_lines=True
                        )

                progress_bar.empty()
                # Download as CSV
                if all_shortlisted:
                    df = pd.DataFrame(all_shortlisted)
                    st.download_button(
                        "Download Shortlisted as CSV",
                        df.to_csv(index=False),
                        file_name="shortlisted_candidates.csv",
                        help="Download the shortlisted candidates as a CSV file.",
                    )
                else:
                    st.warning("No Sutable candidates found for given requirements")

        else:
            st.error("CSV must contain 'Job Title' and 'Job Description' columns.")
    else:
        st.error("Please upload JD CSV and at least one resume.")


with st.expander("📊 Screening Records"):
    try:
        conn_sidebar = sqlite3.connect("db/job_screening.db", check_same_thread=False)
        last_refresh = st.button(
            "🔄 Refresh Records",
            help="Refresh the table to fetch the latest screening results.",
        )
        if last_refresh or True:
            df_matches = pd.read_sql_query("SELECT * FROM matches", conn_sidebar)
            st.dataframe(df_matches, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(
            "No data to show yet. Upload and run a screening to populate results."
        )

st.markdown("""
---
<center>© 2025 Tathagata Chakraborty. All rights reserved.</center>
""",unsafe_allow_html=True)
