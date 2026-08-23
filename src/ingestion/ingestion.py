"""
Document ingestion pipeline.

Responsibilities:
- Load supported documents from the knowledge base.
- Split documents into chunks suitable for retrieval.
- Build the ChromaDB vector store.

The module intentionally contains no embedding or retrieval logic.
"""

import logging
from pathlib import Path

import frontmatter
import re 

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

# Supported document loaders.
LOADERS = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
}

EMBEDDING_MODEL = "text-embedding-3-large"

def _flatten_metadata(metadata: dict) -> dict:
    """
    Flatten nested dicts/lists in frontmatter metadata into flat scalars,
    since Chroma only accepts str/int/float/bool metadata values.

    - dict values are flattened into `key_subkey` pairs.
    - list-of-dict values are flattened into `key_N_subkey` pairs.
    - lists of scalars (e.g. skills: [...]) are left untouched — Chroma
      accepts homogeneous scalar lists.
    """
    flat: dict = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flat[f"{key}_{sub_key}"] = sub_value
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            for i, item in enumerate(value):
                for sub_key, sub_value in item.items():
                    flat[f"{key}_{i}_{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat

def load_documents(data_dir: Path) -> list[Document]:
    """
    Load all supported documents from a directory.

    Markdown files are parsed for YAML frontmatter (role/project metadata
    used for retrieval filtering); other formats fall back to LangChain
    loaders and get text-cleaned to remove format-specific artifacts.

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

        suffix = path.suffix.lower()

        # Markdown handled separately: frontmatter carries retrieval metadata
        # (industry, skills, dates) that LangChain's loaders don't parse.
        if suffix == ".md":
            try:
                post = frontmatter.load(str(path))
            except Exception as e:
                print(f"Error parsing frontmatter for {path.name}: {e}")
                continue

            if not post.metadata:
                print(f"Warning: {path.name} has no frontmatter metadata")

            metadata = _flatten_metadata(dict(post.metadata))

            documents.append(
                Document(
                    page_content=post.content.strip(),
                    metadata={
                        **metadata,
                        "source": path.name,
                        "file_path": str(path),
                        "file_type": "md",
                        "has_metadata": bool(post.metadata),
                    },
                )
            )
            continue

        loader_cls = LOADERS.get(suffix)
        if loader_cls is None:
            print(f"Skipping unsupported file: {path.name}")
            continue

        loader = loader_cls(str(path))
        loaded_docs = loader.load()
        # Only non-markdown needs cleanup (PDF line-wraps, DOCX repeated
        # newlines) — markdown formatting is author-controlled.
        for doc in loaded_docs:
            doc.page_content = clean_text(doc.page_content)
            doc.metadata.setdefault("source", path.name)
            doc.metadata["file_path"] = str(path)
            doc.metadata["file_type"] = suffix.lstrip(".")
        documents.extend(loaded_docs)

    return documents


MARKDOWN_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def split_documents(documents: list[Document], *, chunk_size: int = 500, chunk_overlap: int = 100) -> list[Document]:
    """
    Split documents into overlapping chunks.

    Markdown documents are split on header boundaries first (preserving
    role/project section structure and frontmatter metadata), then
    re-split by size as a safety net. Other formats use character-based
    splitting directly.

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
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=MARKDOWN_HEADERS,
        strip_headers=False,  # keep header text in content for chunk-level context
    )

    chunks: list[Document] = []
    for doc in documents:
        if doc.metadata.get("file_type") == "md":
            # Split on headers first, merging original metadata (industry,
            # skills, dates, source) with the header-path metadata added
            # by the splitter (h1/h2/h3).
            header_chunks = header_splitter.split_text(doc.page_content)
            for hc in header_chunks:
                hc.metadata = {**doc.metadata, **hc.metadata}
            # Safety net: re-split any section still over chunk_size.
            chunks.extend(char_splitter.split_documents(header_chunks))
        else:
            chunks.extend(char_splitter.split_documents([doc]))

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