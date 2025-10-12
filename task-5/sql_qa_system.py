import os
import re
import sqlite3
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

# Load and set environment variables
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env (Gemini API key)")
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

DB_PATH = os.getenv("DB_PATH", "portfolio.db")
os.environ["DB_PATH"] = DB_PATH





app = FastAPI(title="Task-05 SQL QA - FastAPI")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

PROMPT_TEMPLATE = """
You are a SQL generator assistant for a SQLite database. Use the exact table schemas below to create a READ-ONLY SQL query (only SELECTs) that answers the user's question. 
Return **only the SQL** in a code block (triple backticks) or "NO_SQL" if not possible.

Schema:
{table_info}

Instructions:
- Do NOT output explanations.
- Only SELECT, FROM, JOIN, WHERE, GROUP BY, ORDER BY, LIMIT.
- Use ISO date format for date comparisons (YYYY-MM-DD).
- When ambiguous, prefer safe SELECT with LIMIT 100.
- If no data or unrelated question, respond "NO_SQL".

User question:
{user_question}
"""

prompt = PromptTemplate(input_variables=["table_info", "user_question"], template=PROMPT_TEMPLATE)
chain = prompt | llm

# ----------------------------
# Safety checks
# ----------------------------
FORBIDDEN_TOKENS = ["drop ", "delete ", "update ", "alter ", "insert ", "create ", ";--", "--", "truncate "]

def extract_sql(text: str) -> str:
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"(select\b.*)", text, flags=re.IGNORECASE | re.DOTALL)
    return m2.group(1).strip() if m2 else ""

def is_safe_sql(sql_text: str) -> bool:
    sql_lower = sql_text.lower()
    return sql_lower.strip().startswith("select") and not any(tok in sql_lower for tok in FORBIDDEN_TOKENS)

def get_table_info_sqlite(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = []
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for (tname,) in cur.fetchall():
        if tname.startswith("sqlite_"):
            continue
        cur.execute(f"PRAGMA table_info('{tname}')")
        cols = cur.fetchall()
        col_strs = [f"{c[1]} {c[2]}" for c in cols]
        tables.append(f"Table {tname}: ({', '.join(col_strs)})")
    conn.close()
    return "\n".join(tables)

def run_sql(db_path: str, sql_text: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql_text)
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return rows

# ----------------------------
# Request body
# ----------------------------
class QueryRequest(BaseModel):
    query: str

# ----------------------------
# FastAPI endpoints
# ----------------------------
@app.post("/query")
async def query_endpoint(req: QueryRequest):
    user_q = req.query.strip()
    if not user_q:
        return {"error": "Empty query"}

    table_info = get_table_info_sqlite(DB_PATH)
    llm_input = {"table_info": table_info, "user_question": user_q}
    sql_raw = chain.invoke(llm_input)

    # Query preparation
    sql_text= str(sql_raw)
    sql_candidate = extract_sql(sql_text)
    sql_candidate = sql_candidate.encode().decode('unicode_escape')
    

    if not sql_candidate or sql_candidate.upper() == "NO_SQL":
        return {"query": user_q, "sql": None, "answer": "Cannot generate SQL for this question."}

    if is_safe_sql(sql_candidate):
        try:
            rows = run_sql(DB_PATH, sql_candidate)
        except Exception as e:
            return {"query": user_q, "sql": sql_candidate, "error": str(e)}
        return {"query": user_q, "sql": sql_candidate, "rows": rows, "row_count": len(rows)}
    else:
        return {"query": user_q, "sql": sql_candidate, "answer": "Generated SQL rejected by safety filter."}

    

@app.get("/")
async def root():
    return {"message": "SQL QA System is running."}
