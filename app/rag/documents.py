from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "data" / "medical_knowledge"


def load_documents() -> list[Document]:
    docs = []
    for path in KNOWLEDGE_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
    )
    return splitter.split_documents(docs)
