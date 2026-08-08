"""
Document ingestion pipeline.

Responsibilities:
- Load supported documents from the knowledge base.
- Split documents into chunks suitable for retrieval.
- Build the ChromaDB vector store.

The module intentionally contains no embedding or retrieval logic.
"""

from pathlib import Path
import re 

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


# Supported document loaders.
LOADERS = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": TextLoader,
    ".txt": TextLoader,
}

EMBEDDING_MODEL = "text-embedding-3-large"

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

    chunks = splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")

    return chunks

def clean_text(text):
    # Collapse single newlines (likely mid-sentence wraps) into spaces,
    # but preserve intentional paragraph breaks (blank lines).
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Collapse 3+ newlines down to a standard paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse repeated spaces/tabs.
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def build_vector_store(documents: list[Document], vector_store_path: Path,
    *,
    embedding_model: str = EMBEDDING_MODEL) -> Chroma:
    """
    Create a ChromaDB vector store from document chunks.

    Parameters
    ----------
    documents
        Chunked knowledge-base documents.

    vector_store_path
        Directory where ChromaDB will persist its data.

    embedding_model
        OpenAI embedding model used for indexing.

    Returns
    -------
    Chroma
        Initialized ChromaDB vector store.
    """

    embeddings = OpenAIEmbeddings(model=embedding_model)

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(vector_store_path),
    )

    return vector_store

def ensure_vector_store(data_dir: Path, vector_store_path: Path) -> Chroma:
    """Load an existing vector store or build it if necessary."""

    if vector_store_path.exists():
        return Chroma(persist_directory=str(vector_store_path),
            embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        )

    print("Vector store not found. Building knowledge base...")

    documents = load_documents(data_dir)
    chunks = split_documents(documents)

    return build_vector_store(documents=chunks, vector_store_path=vector_store_path)