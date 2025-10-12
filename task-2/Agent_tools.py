import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_experimental.utilities.python import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

# -------------------------------
# Step 1: Set up API key
# -------------------------------
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY") 

# -------------------------------
# Step 2: Initialize LLM
# -------------------------------
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# -------------------------------
# Step 3: Define Tools
# -------------------------------

# Tool 1: Safe Calculator
def simple_calculator(expression: str) -> str:
    try:
        # Restrict eval for safety
        allowed_chars = "0123456789+-*/(). "
        if not all(char in allowed_chars for char in expression):
            return "Error: Only basic math operations allowed."
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

calculator_tool = Tool(
    name="Calculator",
    func=simple_calculator,
    description="Useful for evaluating mathematical expressions."
)

# Tool 2: Python REPL
python_repl = PythonREPL()
python_tool = Tool(
    name="Python REPL",
    func=python_repl.run,
    description="Executes Python code directly."
)

# Tool 3: DuckDuckGo Search
search_tool = DuckDuckGoSearchRun()

tools = [calculator_tool, python_tool, search_tool]

# -------------------------------
# Step 4: Initialize Agent
# -------------------------------
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -------------------------------
# Step 5: Streamlit UI
# -------------------------------
st.title("🧮 Tools Calculator")

queries = [
    "Segment 10,000 customers into 3 groups by engagement: high, medium, low.",
    "Forecast ROI if investment is 50000 with 12% growth over 5 years using compound interest.",
    "Get the latest news about AI in marketing.",
    "Write a Python function to calculate churn probability using logistic function."
]

selected_query = st.selectbox("Choose a sample query:", [""] + queries)
user_input = st.text_input("Or write your own query:")
final_query = user_input if user_input else selected_query

if final_query:
    with st.spinner("Processing your query..."):
        response = agent.run(final_query)
    st.write("### 🧠 Response:")
    st.write(response)
