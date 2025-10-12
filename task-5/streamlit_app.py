
# streamlit_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("LOCAL_API_URL", "http://localhost:8000/query")
os.environ["API_URL"] = API_URL

st.set_page_config(page_title="SQL QA Demo", layout="wide")
st.title("SQL QA Demo — Task 05")

queries = [
    "List top 5 campaigns by ROI in the last 6 months.",
    "Which channels drive the most conversions for campaigns with spend > 50000?",
    "Show customers in Urban region with loyalty_score > 80 sorted by churn_risk desc.",
    "How many leads were converted per campaign?",
    "Top 10 campaigns targeting 'social' channel by conversions per rupee spent."]
selected_query = st.selectbox("Choose a sample query: " , [""]+ queries)
user_input = st.text_input("Ask a question about campaigns/customers/leads (example: 'Top 5 campaigns by ROI in the last 6 months')")

q = user_input if user_input else selected_query

if st.button("Run Query"):
    if not q.strip():
        st.warning("Please type a question.")
    else:
        with st.spinner("Querying..."):
            resp = requests.post(API_URL, json={"query": q})
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    st.subheader("Generated Sql")
                    st.code(data.get("sql") or "No Sql generated", language= "sql")
                    st.subheader("Result")
                    rows = data.get("rows", [])
                    if not rows:
                        st.write("No rows returned")
                    else:
                        st.dataframe(rows)
                    st.write(f"Row count: {data.get('row_count', 0)}")
                except Exception as e:
                    st.error(f"Response is not valid Json: {e}")
            else:
                st.error(f"API error: {resp.status_code} - {resp.text}")
            