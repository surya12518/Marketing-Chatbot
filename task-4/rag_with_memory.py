import os
import numpy as np
import faiss
import streamlit as st
import asyncio
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from google import generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.vectorstores import FAISS as LangChainFAISS
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from streamlit_chat import message

# Load environment variables from .env file
load_dotenv()
# Initialize Google Generative AI with API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Asyncio
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

# Function to create LangChain-compatible FAISS vector store
def create_langchain_vectorstore(chunks):
    if not chunks:
        raise ValueError("No text chunks to index.")
    documents = [Document(page_content=chunk) for chunk in chunks]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = LangChainFAISS.from_documents(documents, embeddings)
    return vectorstore

# Function to create conversational chain with memory
def create_conversational_chain(vectorstore):
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3
    )
    retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        llm=llm
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=True
    )
    return qa_chain

# Function to retrieve relevant chunks using FAISS of the query
def retrieve_chunks(query, index, chunks, k=5):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(np.array(query_embedding).astype('float32'), k)
    return [chunks[i] for i in indices[0]]


import streamlit as st

# --- Your existing imports ---
# from your_module import load_pdf, chunk_text, create_faiss_index, create_langchain_vectorstore, create_conversational_chain, retrieve_chunks

# --- Initialize session state ---
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "index" not in st.session_state:
    st.session_state.index = None
if "chunk_list" not in st.session_state:
    st.session_state.chunk_list = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- Streamlit UI ---
st.title("📊 Campaign Data QA Bot")
st.write("Upload a marketing campaign PDF and ask questions interactively!")

# --- PDF Upload ---
uploaded_file = st.file_uploader("📁 Upload your campaign PDF", type=["pdf"])

if uploaded_file is not None and st.session_state.qa_chain is None:
    with st.spinner("Processing PDF..."):
        campaign_text = load_pdf(uploaded_file)
        chunks = chunk_text(campaign_text, chunk_size=100, overlap=20)
        index, chunk_list = create_faiss_index(chunks)
        vectorstore = create_langchain_vectorstore(chunks)
        qa_chain = create_conversational_chain(vectorstore)

        # Save to session
        st.session_state.qa_chain = qa_chain
        st.session_state.index = index
        st.session_state.chunk_list = chunk_list

    st.success("✅ PDF successfully processed! You can now chat with the bot.")


# --- Chat Section ---
st.subheader("💬 Chat with your Campaign QA Bot")

def chat_with_bot():
    query = st.session_state.query
    qa_chain = st.session_state.qa_chain
    if qa_chain is None:
        st.session_state.history.append([query, "⚠️ Please upload a PDF first."])
        return
    if not query.strip():
        st.session_state.history.append([query, "⚠️ Enter a valid message."])
        return
    response = qa_chain({"question": query})
    st.session_state.history.append([query, response["answer"]])
    st.session_state.query = ""  # Clear input after sending


# --- Display Chat History ---
if st.session_state.history:
    for user_msg, bot_msg in st.session_state.history:
        st.markdown(f"**You:** {user_msg}")
        st.markdown(f"**Bot:** {bot_msg}")
        st.markdown("---")

# Text input with on_change triggers chat
st.text_input("Ask a question about the marketing data:", key="query", on_change=chat_with_bot)

st.title("Document QA on Brand & Campaign Documents")

# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = None
    st.session_state.chunks = None
    st.session_state.vectorstore = None
    st.session_state.qa_chain = None
    st.session_state.chat_history = []

if 'generated' not in st.session_state:
    st.session_state.generated = []

if 'past' not in st.session_state:
    st.session_state.past = []

# Sidebar for document upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        text = load_pdf(uploaded_file)
        chunks = chunk_text(text)
        index, chunks = create_faiss_index(chunks)
        vectorstore = create_langchain_vectorstore(chunks)
        qa_chain = create_conversational_chain(vectorstore)
        st.session_state.index = index
        st.session_state.chunks = chunks
        st.session_state.vectorstore = vectorstore
        st.session_state.qa_chain = qa_chain
        st.session_state.chat_history = []
        st.success("Document processed and indexed with memory enabled!")
    if st.session_state.qa_chain is not None:
        if st.button("Clear Conversation History"):
            st.session_state.chat_history = []
            st.session_state.generated = []
            st.session_state.past = []
            st.session_state.qa_chain = create_conversational_chain(st.session_state.vectorstore)
            st.success("Conversation history cleared!")

def process_question():
    if st.session_state.input and st.session_state.qa_chain is not None:
        with st.spinner("Retrieving answer with context memory..."):
            try:
                result = st.session_state.qa_chain({"question": st.session_state.input})
                answer = result["answer"]
                st.session_state.chat_history.append({
                    "question": st.session_state.input,
                    "answer": answer
                })
                st.session_state.past.append(st.session_state.input)
                st.session_state.generated.append(answer)
                st.session_state.input = ""
            except Exception as e:
                st.error(f"Error generating answer: {str(e)}")
    elif st.session_state.input:
        st.warning("Please upload a document first.")

# Display current answer if available
if st.session_state.generated:
    # Optionally show source documents from the last result
    if st.session_state.qa_chain is not None and st.session_state.input:
        try:
            result = st.session_state.qa_chain({"question": st.session_state.input})
            if "source_documents" in result:
                with st.expander("View Source Documents"):
                    for i, doc in enumerate(result["source_documents"][:3]):
                        st.write(f"**Source {i+1}:**")
                        st.write(doc.page_content[:300] + "...")
        except:
            pass

# Display conversation history in chat format
if st.session_state['generated']:
    for i in range(len(st.session_state.generated)):
        message(st.session_state.past[i], is_user=True, key=str(i) + '_user')
        message(st.session_state.generated[i], key=str(i),
                avatar_style="adventurer", seed=123)

user_input = st.text_input("Enter Your Question about document: ", key="input", on_change=process_question)