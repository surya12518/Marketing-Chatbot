# 🎯 Marketing Analytics Chatbot

**An intelligent AI-powered chatbot that helps marketers analyze campaign performance and extract data-driven insights from marketing metrics.**

---

## 🏢 Project Overview

This project was developed as part of the **MarketGen GenAI Rollout**, where our goal was to integrate **Generative AI capabilities** into the existing marketing analytics workflow.  
The system enables marketers to **chat with their data**, retrieve campaign insights, analyze performance, and compare results — all in a conversational interface powered by **Google Gemini** and **LangChain**.

---

## 🧠 Core Objectives

- Build a **marketing chatbot** with conversational memory.  
- Enable **document-based question answering (RAG)** over campaign briefs and brand manuals.  
- Extend RAG with **memory and multi-step query retrieval**.  
- Create an **SQL QA system** for campaign and customer data.  
- Implement a **summarization engine** for marketing reports and survey feedback.  

---

## 👥 Team Contributions

| Team Member | Tasks Completed | Description |
|--------------|----------------|--------------|
| **Surymani** | ✅ Task 1, 3, 4, 6, 8 | Built the **Marketing Chatbot with Memory**, implemented **RAG (Basic)** and **RAG with Conversational Memory & Multi-Query Retrieval** using LangChain and Gemini. |
| **Dhruve** | ✅ Task 5, 2 | Developed the **SQL QA System** for querying campaign data in natural language and the **Summarization Engine** for condensing marketing reports using Gemini. |

---
### 1. Create Project Directory
```bash
mkdir marketing-chatbot
cd marketing-chatbot
```
### 2. Set Up Virtual Environment
```bash
python -m venv venv

# Activate on Mac/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure Environment
- Create a .env file:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
### 5. Running the Application
- Save the Code
- for graido
```bash
python <filename>
```
- For streamlit
```bash
streamlit run <filename>
```
### Access the interface
- The terminal will display a local URL
- Open this URL in your web browser
- Start chatting with the marketing analytics assistant!
## 🧩 System Architecture

## 🔧 Core Components

### 1. Advanced Document Processing
- 📄 PDF text extraction using **PyPDF2**  
- ✂️ Intelligent chunking with overlap  
- 🧱 **LangChain** document structuring for RAG  

### 2. Multi-Query Retrieval System
- 🔁 Generates multiple query variations for better recall  
- 🎯 Improves search relevance through query expansion  
- 🧩 Retrieves diverse contextual information  

### 3. Conversational Memory
- 💬 Maintains chat history using **ConversationBufferMemory**  
- 🧠 Enables follow-up questions and contextual understanding  
- 🔒 Preserves conversation context across interactions  

### 4. Intelligent Vector Search
- ⚡ **FAISS** for fast similarity search  
- 🧩 **HuggingFace** embeddings for semantic understanding  
- 🧭 Efficient retrieval of relevant document sections  

### 5. Streamlit Chat Interface
- 🪶 Interactive chat-style interface  
- 💬 Real-time Q&A  
- 🧾 Session-based memory management  

## ⚡ Key Features

- 🧠 **Conversational Memory** — Remembers context for follow-up questions  
- 🤖 **Multi-Query Intelligence** — Reformulates queries for better retrieval  
- 📘 **Document Understanding** — Reads campaign briefs and marketing documents  
- 🗣️ **Contextual Responses** — Generates responses based on previous conversations  
- 📊 **Comparative Analysis** — Can contrast different campaigns dynamically  

---

## 📊 What It Does

The **Marketing Analytics Chatbot** acts as an **AI-driven marketing analyst** that can:

- Process and understand campaign briefs, reports, and brand manuals  
- Answer analytical queries about campaigns and budgets  
- Retrieve relevant information using **vector similarity search**  
- Generate **context-aware insights**  
- Compare performance across campaigns  

> 💡 The system blends **Retrieval-Augmented Generation (RAG)** with **Conversational Memory**, enabling marketers to have meaningful, context-rich AI interactions.

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **LLM** | Google Gemini Pro |
| **Framework** | LangChain |
| **Embeddings** | HuggingFace SentenceTransformer |
| **Vector Store** | FAISS |
| **Frontend** | Streamlit / Gradio |
| **Memory** | ConversationBufferMemory |
| **Database (Task 5)** | SQLite |
| **Summarization (Task 6)** | LangChain Summarization Chains (MapReduce / Refine) |
