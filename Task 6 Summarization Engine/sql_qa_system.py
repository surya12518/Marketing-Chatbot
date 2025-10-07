from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import os

# LangChain + Gemini/OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase

# Load API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# FastAPI app
app = FastAPI(title="SQL QA System - Task 06")

# Connect DB
db = SQLDatabase.from_uri("sqlite:///portfolio.db")

# Load LLM (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

# Create chain
chain = create_sql_query_chain(llm, db)

# Request body
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_db(request: QueryRequest):
    user_query = request.query

    # Generate SQL
    sql_query = chain.invoke({"question": user_query})

    # Run SQL
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    conn.close()

    return {"query": user_query, "sql": sql_query, "results": rows}
