import streamlit as st
import requests

st.set_page_config(page_title="SQL QA System", layout="centered")

st.title("💡 Task-06 SQL QA System")
st.write("Ask questions in natural language, get SQL + results.")

query = st.text_input("Enter your question:")

if st.button("Run Query"):
    if query.strip():
        try:
            response = requests.post(
                "http://localhost:8000/query",
                json={"query": query}
            )
            data = response.json()

            st.subheader("📝 Generated SQL:")
            st.code(data["sql"], language="sql")

            st.subheader("📊 Results:")
            st.write(data["results"])

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question.")
