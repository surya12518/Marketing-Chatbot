import os
from dotenv import load_dotenv
import streamlit as st
from typing import Annotated, List, Literal, TypedDict
from PyPDF2 import PdfReader
import asyncio
import time

# LangChain & LLMs
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import acollapse_docs, split_list_of_docs
from langchain_core.documents import Document
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
import operator
from google.api_core.exceptions import ResourceExhausted

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
os.environ["api_key"] = api_key

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("📄 Document Loader & Summarizer")

option = st.selectbox("Select input type", options=["URL", "PDF"])
docs_text = []

def load_pdf(files):
    text = ""
    for file in files:
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Document loader
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

# Main action button
if st.button("Load & Summarize Document"):
    # Load document
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

    # ----------------------------
    # LLM & Graph Setup
    # ----------------------------
    llm = GoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1200)
    split_docs = [Document(page_content=t) for t in docs_text]
    split_docs = text_splitter.split_documents(split_docs)

    # Map & reduce prompts including user objective
    map_template = "Write a concise summary of the following:\n\n{context}"
    reduce_template = """
    The following is a set of summaries:
    {docs}
    Take these and distill it into a final, consolidated summary
    of the main themes.
    """
    if user_prompt:
        map_template += f"\n\nObjective: {user_prompt}"
        reduce_template += f"\n\nObjective: {user_prompt}"

    map_prompt = ChatPromptTemplate.from_messages([("human", map_template)])
    map_chain = map_prompt | llm | StrOutputParser()

    reduce_prompt = ChatPromptTemplate([("human", reduce_template)])
    reduce_chain = reduce_prompt | llm | StrOutputParser()

    token_max = 1200

    # ----------------------------
    # Helper functions
    # ----------------------------
    def lenght_function(documents: List[Document]) -> int:
        return sum(llm.get_num_tokens(doc.page_content) for doc in documents)

    class overallState(TypedDict):
        contents: List[str]
        summaries: Annotated[List[str], operator.add]
        collapsed_summaries: List[Document]
        final_summary: str

    initial_state = {
        "contents": [doc.page_content for doc in split_docs],
        "summaries": [],
        "collapsed_summaries": [],
        "final_summary": ""
    }

    class summaryState(TypedDict):
        content: str

    async def invoke_with_retry(chain, content, retries=3, delay=5):
        for attempt in range(retries):
            try:
                return await chain.ainvoke(content)
            except ResourceExhausted:
                st.warning(f"Quota exceeded. Retrying in {delay} seconds... (Attempt {attempt+1})")
                time.sleep(delay)
        raise RuntimeError("Quota exceeded, failed after retries")

    async def generate_summary(state: summaryState):
        response = await invoke_with_retry(map_chain, state["content"])
        return {"summaries": [response]}

    def map_summaries(state: overallState):
        return [Send("generate_summary", {"content": content}) for content in state["contents"]]

    def collect_summaries(state: overallState):
        return {"collapsed_summaries": [Document(summary) for summary in state["summaries"]]}

    async def collapse_summaries(state: overallState):
        doc_lists = split_list_of_docs(state["collapsed_summaries"], lenght_function, token_max)
        results = []
        for doc_list in doc_lists:
            results.append(await acollapse_docs(doc_list, lambda c: invoke_with_retry(reduce_chain, c)))
        return {"collapsed_summaries": results}

    def should_collapse(state: overallState) -> Literal["collapse_summaries", "generate_final_summary"]:
        collapsed = state.get("collapsed_summaries", [])
        num_token = lenght_function(collapsed)
        if num_token > token_max:
            return "collapse_summaries"
        else:
            return "generate_final_summary"

    async def generate_final_summary(state: overallState):
        collapsed = state.get("collapsed_summaries", [])
        response = await invoke_with_retry(reduce_chain, collapsed)
        return {"final_summary": response}

    # ----------------------------
    # Construct the graph
    # ----------------------------
    graph = StateGraph(overallState)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("collect_summaries", collect_summaries)
    graph.add_node("collapse_summaries", collapse_summaries)
    graph.add_node("generate_final_summary", generate_final_summary)

    graph.add_conditional_edges(START, map_summaries, ["generate_summary"])
    graph.add_edge("generate_summary", "collect_summaries")
    graph.add_conditional_edges("collect_summaries", should_collapse)
    graph.add_conditional_edges("collapse_summaries", should_collapse)
    graph.add_edge("generate_final_summary", END)

    app_graph = graph.compile()

    # ----------------------------
    # Display Graph
    # ----------------------------
    st.subheader("📊 Workflow Graph")
    img_data = app_graph.get_graph().draw_mermaid_png()
    st.image(img_data, caption="LangGraph Workflow")

    # ----------------------------
    # Run the Graph
    # ----------------------------
    st.subheader("🧠 Running Workflow...")

    async def run_graph():
        steps = []
        async for step in app_graph.astream(initial_state, {"recursion": 5}):
            steps.append(step)
        return steps

    steps = asyncio.run(run_graph())
    st.success("✅ Summary generation complete!")

    # ----------------------------
    # Display Final Summary
    # ----------------------------
    st.subheader("📜 Final Summary")
    if steps:
        summary = next(iter(steps[-1].values()))
        st.write(summary.get("final_summary", "Summary Not generated"))
    


