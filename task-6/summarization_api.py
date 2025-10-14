# task-6/summarization_api.py
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from summarization_core import summarize_documents, load_pdf
from langchain_community.document_loaders import WebBaseLoader
import io

app = FastAPI(title="Summarization API")

# ----------------------------
# 1️⃣ JSON input (plain text)
# ----------------------------
class SummarizeRequest(BaseModel):
    docs: list[str]
    objective: str = "Summarize this document"

@app.post("/summarize_json")
async def summarize_json_api(request: SummarizeRequest):
    """
    Endpoint for JSON-friendly text input (Streamlit / n8n)
    """
    try:
        summary = await summarize_documents(request.docs, request.objective)
        return JSONResponse({"summary": summary})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ----------------------------
# 2️⃣ Form/file input (PDF or URL)
# ----------------------------
@app.post("/summarize")
async def summarize_form_api(
    option: str = Form(...),            # "PDF" or "URL"
    url: str = Form(None),
    objective: str = Form("Summarize this document"),
    file: UploadFile = File(None)
):
    try:
        docs_text = []

        # URL input
        if option == "URL" and url:
            loader = WebBaseLoader(url)
            docs = loader.load()
            docs_text = [doc.page_content for doc in docs]

        # PDF input
        elif option == "PDF" and file:
            pdf_bytes = await file.read()
            docs_text = [load_pdf([io.BytesIO(pdf_bytes)])]

        else:
            return JSONResponse({"error": "Invalid input"}, status_code=400)

        # Generate summary
        summary = await summarize_documents(docs_text, objective)
        return JSONResponse({"summary": summary})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ----------------------------
# Run API server
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
