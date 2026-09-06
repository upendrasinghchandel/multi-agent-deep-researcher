import os
from langchain_core.documents import Document
from pypdf import PdfReader
from docx import Document as DocxDocument

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_chunk_document(file_path: str) -> list[Document]:
    """Parses local PDF, TXT, MD, or DOCX files and chunks them for vector storage."""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".docx":
            doc = DocxDocument(file_path)
            text = "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception:
        return []

    if not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.create_documents(
        texts=[text],
        metadatas=[{"source_file": os.path.basename(file_path)}]
    )