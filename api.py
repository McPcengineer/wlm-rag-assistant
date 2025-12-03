import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# --- Load environment variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- FastAPI app ---
app = FastAPI(title="WLM RAG Assistant API")

# --- Request Model ---
class QuestionRequest(BaseModel):
    question: str

# --- CONFIG ---
CHROMA_PATH = "./chroma_db"

# Load embeddings
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Load vector DB
db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_function
)

# LLM (Groq)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    groq_api_key=GROQ_API_KEY
)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are an expert in Blue Yonder WLM (Warehouse Labor Management).
Answer ONLY based on the provided context.
If the answer is not in the context, say: "No tengo suficiente información para responder eso."

Question:
{question}

Context:
{context}

Answer:
""")

# --- RAG FUNCTION ---
def ask_rag(question: str):
    # similarity search
    results = db.similarity_search(question, k=4)
    context = "\n\n".join([r.page_content for r in results])

    chain = prompt | llm
    answer = chain.invoke({"question": question, "context": context})

    return {
        "question": question,
        "answer": answer.content,
        "chunks_used": len(results)
    }

# --- API ROUTE ---
@app.post("/ask")
def ask(request: QuestionRequest):
    return ask_rag(request.question)

