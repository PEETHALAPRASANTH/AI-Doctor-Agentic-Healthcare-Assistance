from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from .documents import load_documents
from ..config import get_settings

INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "vectorstore"


def build_vectorstore() -> FAISS:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    documents = load_documents()
    if not documents:
        raise RuntimeError("No knowledge documents were found.")

    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model="text-embedding-3-small",
    )
    store = FAISS.from_documents(documents, embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))
    return store


def load_vectorstore() -> FAISS:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    if not (INDEX_DIR / "index.faiss").exists():
        return build_vectorstore()

    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model="text-embedding-3-small",
    )
    return FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def search_knowledge(query: str, k: int = 4):
    store = load_vectorstore()
    return store.similarity_search(query, k=k)
