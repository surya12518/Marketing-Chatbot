# task-6/summarizationEngine.py
from summarization_core import summarize_documents, load_pdf
import asyncio
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

# (keep all your existing imports and UI setup)
option = st.selectbox("Select input type", options=["URL", "PDF"])
docs = []

if option == "URL":
    url_input = st.text_input("Enter URL here")
elif option == "PDF":
    uploaded_files = st.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True
    )

# User prompt
user_prompt = st.text_area(
    "Enter your summarization objective (e.g., 'Summarize 5000 survey responses into top 5 customer concerns')"
)

if st.button("Load & Summarize Document"):
    if option == "URL" and url_input:
        loader = WebBaseLoader(url_input)
        docs = loader.load()
        docs_text = [doc.page_content for doc in docs]
    elif option == "PDF" and uploaded_files:
        text = load_pdf(uploaded_files)
        docs_text = [text]

    if not docs_text:
        st.error("No document found. Please upload or provide a valid URL.")
        st.stop()

    st.success("Document loaded successfully!")

    st.subheader("🧠 Running Workflow...")
    summary = asyncio.run(summarize_documents(docs_text, user_prompt))
    st.success("✅ Summary generation complete!")
    st.write(summary)
