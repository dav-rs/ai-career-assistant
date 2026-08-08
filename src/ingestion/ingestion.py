"""
Document ingestion pipeline.

Responsibilities:
- Load supported documents from the knowledge base.
- Split documents into chunks suitable for retrieval.

The module intentionally contains no embedding or retrieval logic.
"""

from pathlib import Path
import re 

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Supported document loaders.
LOADERS = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": TextLoader,
    ".txt": TextLoader,
}


def load_documents(data_dir: Path) -> list[Document]:
    """
    Load all supported documents from a directory.

    Parameters
    ----------
    data_dir
        Directory containing the knowledge base.

    Returns
    -------
    list[Document]
        Loaded LangChain documents.
    """

    documents: list[Document] = []

    for path in sorted(data_dir.rglob("*")):

        if path.is_dir():
            continue

        loader_cls = LOADERS.get(path.suffix.lower())

        if loader_cls is None:
            print(f"Skipping unsupported file: {path.name}")
            continue

        loader = loader_cls(str(path))
        documents.extend(loader.load())

    # Clean the page content of every loaded document
    for doc in documents:
        doc.page_content = clean_text(doc.page_content)

    return documents


def split_documents(documents: list[Document], *, chunk_size: int = 500, chunk_overlap: int = 100) -> list[Document]:
    """
    Split documents into overlapping chunks.

    Parameters
    ----------
    documents
        Loaded LangChain documents.

    chunk_size
        Maximum number of characters per chunk.

    chunk_overlap
        Number of overlapping characters between adjacent chunks.

    Returns
    -------
    list[Document]
        Chunked documents.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return splitter.split_documents(documents)

def clean_text(text):
    # Collapse single newlines (likely mid-sentence wraps) into spaces,
    # but preserve intentional paragraph breaks (blank lines).
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Collapse 3+ newlines down to a standard paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse repeated spaces/tabs.
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()