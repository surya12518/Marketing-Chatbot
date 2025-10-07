import os
import numpy as np
import faiss
import streamlit as st
import asyncio
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from google import generativeai as genai
from langchain.chains import RetrievalQA


# Load environment variables from .env file
load_dotenv()
# Initialize Google Generative AI with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Asyncroi
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

def load_pdf(file):
    text = ""
    pdf = PdfReader(file)
    for page in pdf.pages:
        text += page.extract_text() or ""
    return text

# Function to chunk text into smaller pieces
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

# Function to create embeddings and build FAISS index
def create_faiss_index(chunks):
    if not chunks:
        raise ValueError("No text chunks to index. Please check your PDF or chunking logic.")
    embeddings = embedding_model.encode(chunks)
    if len(embeddings.shape) == 1:
        raise ValueError("Embedding model returned 1D embeddings. Check input chunks.")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index, chunks

# Function to retrieve relevant chunks using FAISS of the query
def retrieve_chunks(query, index, chunks, k=5):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(np.array(query_embedding).astype('float32'), k)
    return [chunks[i] for i in indices[0]]

# Function to generate answer using Google Gemini
def generate_answer(query, context):

    full_prompt = f"""
Answer the question using only the information provided in the context. Be accurate and detailed.
if the answer is not in the context, say "The answer is not available in the provided context".
Context: {context}
Question: {query}
Answer:
"""
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(full_prompt)
    return response.text

# Streamlit UI
def main():
    st.set_page_config(page_title="Document QA with Google Gemini", layout="wide")
    st.title("Document QA on Brand & Campaign Documents")

    if 'index' not in st.session_state:
        st.session_state.index = None
        st.session_state.chunks = None

    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        if uploaded_file:
            text = load_pdf(uploaded_file)
            chunks = chunk_text(text)
            index, chunks = create_faiss_index(chunks)
            st.session_state.index = index
            st.session_state.chunks = chunks
            st.success("Document processed and indexed!")

    user_question = st.text_input("Enter your question about the document:")
    if user_question and st.session_state.index and st.session_state.chunks is not None:
        with st.spinner("Retrieving answer..."):
            relevant_chunks = retrieve_chunks(user_question, st.session_state.index, st.session_state.chunks)
            context = "\n\n".join(relevant_chunks)
            if context:
                answer = generate_answer(user_question, context)
                st.write(answer)
            else:
                st.write("No relevant context found in the document.")
    elif user_question:
        st.warning("Please upload a document first.")

if __name__ == "__main__":
    main()