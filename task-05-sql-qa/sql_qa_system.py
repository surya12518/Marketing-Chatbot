# sql_qa_system.py
import os
import re
import json
import sqlite3
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# load .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
DB_PATH = os.getenv("DB_PATH", "portfolio.db")

if not GOOGLE_API_KEY:
    raise EnvironmentError("Set GOOGLE_API_KEY in .env (Gemini API key)")

# LangChain imports (with helpful error messages if missing)
try:
    from langchain import LLMChain, PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception as e:
    raise ImportError(
        "Missing LangChain or langchain-google-genai. Run: pip install langchain langchain-google-genai google-genai\n"
        f"Original error: {e}"
    )

app = FastAPI(title="Task-05 SQL QA - FastAPI")

# Initialize Gemini-backed LLM (via langchain-google-genai wrapper)
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)

PROMPT_TEMPLATE = """
You are a SQL generator assistant for a SQLite database. Use the exact table schemas below to create a READ-ONLY SQL query (only SELECTs) that answers the user's question. 
Return **only the SQL** in a code block (triple backticks) or nothing if the question cannot be answered with the database.

Schema:
{table_info}

Instructions:
- Do NOT output any explanation or commentary.
- Only use SELECT, FROM, JOIN, WHERE, GROUP BY, ORDER BY, LIMIT.
- Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any DML/DDL.
- Use ISO date format for date comparisons (YYYY-MM-DD).
- When ambiguous, prefer to return a safe SELECT with LIMIT 100.
- If no data or the question is unrelated to the DB, respond with "NO_SQL".

User question:
{user_question}
"""

prompt = PromptTemplate(input_variables=["table_info", "user_question"], template=PROMPT_TEMPLATE)
chain = LLMChain(llm=llm, prompt=prompt)

# Basic SQL safety filter
FORBIDDEN_TOKENS = ["drop ", "delete ", "update ", "alter ", "insert ", "create ", ";--", "--", "truncate "]
SELECT_ALLOWED = re.compile(r"^\s*(?:```sql\s*)?(select\b)", re.IGNORECASE | re.DOTALL)

class QueryRequest(BaseModel):
    query: str

def get_table_info_sqlite(db_path: str) -> str:
    """Return a compact schema description for the prompt."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = []
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cur.fetchall()
    for (tname,) in rows:
        if tname.startswith("sqlite_"):
            continue
        cur.execute(f"PRAGMA table_info('{tname}')")
        cols = cur.fetchall()  # cid, name, type, notnull, dflt_value, pk
        col_strs = [f"{c[1]} {c[2]}" for c in cols]
        tables.append(f"Table {tname}: ({', '.join(col_strs)})")
    conn.close()
    return "\n".join(tables)

def extract_sql(text: str) -> str:
    """Extract SQL from triple-backtick or return the first 'SELECT ...' substring found."""
    # look for ```...```
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # fallback: extract from first SELECT to end or to LIMIT
    m2 = re.search(r"(select\b.*)", text, flags=re.IGNORECASE | re.DOTALL)
    return m2.group(1).strip() if m2 else ""

def is_safe_sql(sql_text: str) -> bool:
    l = sql_text.lower()
    for tok in FORBIDDEN_TOKENS:
        if tok in l:
            return False
    # additional basic check: must start with SELECT
    if not l.strip().startswith("select"):
        return False
    return True

def run_sql(db_path: str, sql_text: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql_text)
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
    finally:
        conn.close()
    return result

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    user_q = req.query.strip()
    if not user_q:
        return {"error": "Empty query"}

    # 1. create table info
    table_info = get_table_info_sqlite(DB_PATH)

    # 2. ask LLM to produce SQL
    llm_input = {"table_info": table_info, "user_question": user_q}
    sql_raw = chain.predict(**llm_input)

    sql_candidate = extract_sql(sql_raw)
    if not sql_candidate or sql_candidate.strip().upper() == "NO_SQL":
        return {"query": user_q, "sql": None, "answer": "I cannot produce a SQL query for this question with the available schema."}

    # 3. validate
    if not is_safe_sql(sql_candidate):
        return {"query": user_q, "sql": sql_candidate, "answer": "Generated SQL rejected by safety filter (contains forbidden statements)."}

    # 4. run (read-only)
    try:
        rows = run_sql(DB_PATH, sql_candidate)
    except Exception as e:
        return {"query": user_q, "sql": sql_candidate, "error": str(e)}

    # 5. return
    return {"query": user_q, "sql": sql_candidate, "rows": rows, "row_count": len(rows)}
