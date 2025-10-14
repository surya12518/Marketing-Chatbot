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
- Develop **workflow automation** with n8n for business process automation.

---

## 👥 Team Contributions

| Team Member | Tasks Completed | Description |
|--------------|----------------|--------------|
| **Surymani** | ✅ Task 1, 3, 4, 8 | Built the **Marketing Chatbot with Memory**, implemented **RAG (Basic)** and **RAG with Conversational Memory & Multi-Query Retrieval** using LangChain and Gemini. |
| **Dhruve** | ✅ Task 5, 2, 6 | Developed the **SQL QA System** for querying campaign data in natural language and the **Summarization Engine** for condensing marketing reports using Gemini. |

---

## 🚀 Quick Installation & Setup

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
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
### 5. Running the Applications
- For Gradio Interfaces :
```bash
python <filename>.py
```
### For Streamlit Interfaces:
```bash
streamlit run <filename>.py
```
### For FastAPI Backend (Task 6):
```bash
cd task-6
uvicorn summarization_api:app --reload
```
### For n8n Integration (Task 8):
```bash
cd task-8
streamlit run n8n.py
```

---

## Access the Interfaces
- The terminal displays local URLs for each application  
- Open these URLs in your web browser  
- Start interacting with the marketing analytics assistants!

---

## 📋 Task Overview

### 🎯 Task 1: Marketing Chatbot with Memory
- **Objective:** Build a conversational chatbot with memory for marketing analytics  
- **Technologies:** LangChain, Google Gemini, ConversationBufferMemory  
- **Features:** Context-aware responses, campaign performance analysis  

### 📄 Task 2: Document Summarization Engine
- **Objective:** AI-powered summarization for marketing documents  
- **Technologies:** LangGraph, Map-Reduce architecture, Async processing  
- **Features:** Multi-source input (URL/PDF), customizable objectives  

### 🔍 Task 3: RAG - Document QA System
- **Objective:** Enable Q&A over brand manuals and campaign documents  
- **Technologies:** FAISS, SentenceTransformer, PyPDF2  
- **Features:** Semantic search, document intelligence  

### 💬 Task 4: RAG with Memory & Multi-Query
- **Objective:** Extend RAG with conversational memory and enhanced retrieval  
- **Technologies:** MultiQueryRetriever, ConversationBufferMemory  
- **Features:** Follow-up questions, contextual understanding  

### 🗃️ Task 5: SQL QA System
- **Objective:** Natural language querying for campaign databases  
- **Technologies:** SQLite, FastAPI, LangChain SQL Agent  
- **Features:** NL-to-SQL conversion, safe query execution  

### ⚡ Task 6: Summarization API
- **Objective:** FastAPI backend for document summarization  
- **Technologies:** FastAPI, LangChain, Async operations  
- **Features:** RESTful API, PDF/URL/Text support, retry mechanisms  

### 🔄 Task 8: Workflow Automation with n8n
- **Objective:** Automate marketing workflows with AI integration  
- **Technologies:** n8n, Ngrok, Streamlit, Webhooks  
- **Features:** Multi-channel notifications, business rule automation  

---

## 🧩 System Architecture

### 🔧 Core Components

1. **Advanced Document Processing**
   - PDF text extraction using PyPDF2  
   - Intelligent chunking with overlap  
   - LangChain document structuring for RAG  

2. **Multi-Query Retrieval System**
   - Generates multiple query variations for better recall  
   - Improves search relevance through query expansion  
   - Retrieves diverse contextual information  

3. **Conversational Memory**
   - Maintains chat history using ConversationBufferMemory  
   - Enables follow-up questions and contextual understanding  
   - Preserves conversation context across interactions  

4. **Intelligent Vector Search**
   - FAISS for fast similarity search  
   - HuggingFace embeddings for semantic understanding  
   - Efficient retrieval of relevant document sections  

5. **Streamlit Chat Interface**
   - Interactive chat-style interface  
   - Real-time Q&A  
   - Session-based memory management  

6. **Workflow Automation**
   - n8n integration for business process automation  
   - Webhook triggers from AI outputs  
   - Multi-channel notifications (Slack, Email, Sheets)  

---

## ⚡ Key Features
- **Conversational Memory:** Remembers context for follow-up questions  
- **Multi-Query Intelligence:** Reformulates queries for better retrieval  
- **Document Understanding:** Reads campaign briefs and marketing documents  
- **Contextual Responses:** Generates responses based on previous conversations  
- **Comparative Analysis:** Contrast different campaigns dynamically  
- **Automation Ready:** Integrates with n8n for workflow automation  
- **Async Processing:** Handles large documents efficiently  
- **Safety First:** SQL injection protection and query validation  

---

## 📊 What It Does
The Marketing Analytics Chatbot acts as an AI-driven marketing analyst that can:
- Process and understand campaign briefs, reports, and brand manuals  
- Answer analytical queries about campaigns and budgets  
- Retrieve relevant information using vector similarity search  
- Generate context-aware insights  
- Compare performance across campaigns  
- Automate business processes based on AI analysis  
- Summarize large documents with specific objectives  
- Query databases using natural language  

> The system blends Retrieval-Augmented Generation (RAG) with Conversational Memory and Workflow Automation, enabling marketers to have meaningful, context-rich AI interactions that drive business actions.

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini 2.5 Flash |
| Framework | LangChain, LangGraph |
| Embeddings | HuggingFace SentenceTransformer |
| Vector Store | FAISS |
| Frontend | Streamlit, Gradio |
| Backend | FastAPI |
| Memory | ConversationBufferMemory |
| Database | SQLite |
| Automation | n8n, Ngrok |
| Document Processing | PyPDF2, WebBaseLoader |
| Async Processing | Asyncio |
| Cocker | Containerization N8N |

---

## 🎯 Business Impact
This integrated system enables marketing teams to:
- Analyze campaign performance through conversational AI  
- Automate routine tasks and alerts based on data insights  
- Scale document processing and summarization capabilities  
- Democratize data access through natural language interfaces  
- Accelerate decision-making with real-time AI-powered insights  

