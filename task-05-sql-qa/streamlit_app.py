# streamlit_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("LOCAL_API_URL", "http://localhost:8000/query")

st.set_page_config(page_title="SQL QA Demo", layout="wide")
st.title("SQL QA Demo — Task 05")

q = st.text_area("Ask a question about campaigns/customers/leads (example: 'Top 5 campaigns by ROI in the last 6 months')", height=120)

if st.button("Run Query"):
    if not q.strip():
        st.warning("Please type a question.")
    else:
        with st.spinner("Querying..."):
            resp = requests.post(API_URL, json={"query": q})
            data = resp.json()
        if resp.status_code != 200:
            st.error(f"API error: {data}")
        else:
            st.subheader("Generated SQL")
            st.code(data.get("sql") or "No SQL generated")
            st.subheader("Result (first 50 rows)")
            rows = data.get("rows", [])
            if not rows:
                st.write("No rows returned")
            else:
                st.dataframe(rows[:50])
            st.write(f"Row count: {data.get('row_count', 0)}")
