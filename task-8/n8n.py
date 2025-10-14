# task-8/n8n_streamlit_full.py
import streamlit as st
import requests
import io

# ----------------------------
# Configuration
# ----------------------------
FASTAPI_JSON_URL = "http://127.0.0.1:8000/summarize_json"  # For plain text
FASTAPI_FORM_URL = "http://127.0.0.1:8000/summarize"       # For PDF / URL
N8N_WEBHOOK_URL = "https://ruinous-gussie-deeper.ngrok-free.dev/webhook-test/streamlit-input"

# ----------------------------
# Initialize session state
# ----------------------------
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "last_type" not in st.session_state:
    st.session_state.last_type = ""

# ----------------------------
# UI
# ----------------------------
st.title("📄 Universal Summarizer → n8n")
input_type = st.selectbox("Select input type", ["Text", "PDF", "URL"])
objective = st.text_input("Summarization goal (optional)")

# ----------------------------
# 1️⃣ Text Input
# ----------------------------
if input_type == "Text":
    user_text = st.text_area("Enter text to summarize:", value=st.session_state.last_input if st.session_state.last_type == "Text" else "")
    if st.button("Generate Summary"):
        if not user_text.strip():
            st.warning("Please enter some text!")
        else:
            with st.spinner("Generating summary..."):
                try:
                    resp = requests.post(
                        FASTAPI_JSON_URL,
                        json={"docs": [user_text], "objective": objective}
                    )
                    if resp.status_code == 200:
                        st.session_state.summary = resp.json().get("summary", "")
                        st.session_state.last_input = user_text
                        st.session_state.last_type = "Text"
                        st.success("✅ Summary generated!")
                    else:
                        st.error(f"FastAPI Error: {resp.status_code} - {resp.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")

# ----------------------------
# 2️⃣ PDF Upload
# ----------------------------
elif input_type == "PDF":
    uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file and st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            try:
                pdf_bytes = uploaded_file.read()
                files = {"file": (uploaded_file.name, io.BytesIO(pdf_bytes), "application/pdf")}
                resp = requests.post(
                    FASTAPI_FORM_URL,
                    files=files,
                    data={"option": "PDF", "objective": objective}
                )
                if resp.status_code == 200:
                    st.session_state.summary = resp.json().get("summary", "")
                    st.session_state.last_input = uploaded_file.name
                    st.session_state.last_type = "PDF"
                    st.success("✅ Summary generated!")
                else:
                    st.error(f"FastAPI Error: {resp.status_code} - {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

# ----------------------------
# 3️⃣ URL Input
# ----------------------------
elif input_type == "URL":
    url_input = st.text_input("Enter URL to summarize:", value=st.session_state.last_input if st.session_state.last_type == "URL" else "")
    if url_input and st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            try:
                resp = requests.post(
                    FASTAPI_FORM_URL,
                    data={"option": "URL", "url": url_input, "objective": objective}
                )
                if resp.status_code == 200:
                    st.session_state.summary = resp.json().get("summary", "")
                    st.session_state.last_input = url_input
                    st.session_state.last_type = "URL"
                    st.success("✅ Summary generated!")
                else:
                    st.error(f"FastAPI Error: {resp.status_code} - {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

# ----------------------------
# Display summary if available
# ----------------------------
if st.session_state.summary:
    st.subheader("Generated Summary")
    st.text_area("Summary", st.session_state.summary, height=200)

    # ----------------------------
    # Send summary to n8n
    # ----------------------------
    if st.button("Send Summary to n8n"):
        with st.spinner("Sending summary to n8n..."):
            try:
                n8n_resp = requests.post(N8N_WEBHOOK_URL, json={"input": objective, "summary": st.session_state.summary})
                if n8n_resp.status_code == 200:
                    st.success("🚀 Summary sent to n8n successfully!")
                    try:
                        st.json(n8n_resp.json())
                    except Exception:
                        st.info("n8n returned non-JSON response (check your workflow output).")
                else:
                    st.error(f"Failed to send to n8n. Status: {n8n_resp.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error sending to n8n: {e}")
