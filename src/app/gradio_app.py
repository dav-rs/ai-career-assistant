"""
Gradio application for the AI Career Assistant.

The application layer is responsible for:
- Initializing the knowledge base.
- Initializing the RAG pipeline.
- Translating Gradio conversation history.
- Rendering answers and supporting sources.

RAG logic remains in the rag package.
Document ingestion remains in the ingestion package.
"""

from pathlib import Path

import gradio as gr
from langchain_core.messages import AIMessage, HumanMessage

from src.ingestion.ingestion import ensure_vector_store
from src.rag.pipeline import RAGPipeline

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "knowledge_base"
VECTOR_STORE_PATH = PROJECT_ROOT / "data" / "vector_db"

TOP_K = 4


# ---------------------------------------------------------------------------
# Knowledge base initialization
# ---------------------------------------------------------------------------

vector_store = ensure_vector_store(data_dir=RAW_DATA_PATH, vector_store_path=VECTOR_STORE_PATH)


# ---------------------------------------------------------------------------
# RAG pipeline initialization
# ---------------------------------------------------------------------------

pipeline = RAGPipeline(vector_store=vector_store, top_k=TOP_K)


# ---------------------------------------------------------------------------
# Conversation handling
# ---------------------------------------------------------------------------

def convert_history(history: list | None) -> list:
    """
    Convert Gradio message history into LangChain messages.

    Gradio uses dictionaries with ``role`` and ``content``.
    The RAG pipeline uses LangChain message objects.
    """

    if not history:
        return []

    messages = []

    for message in history:
        role = message.get("role")
        content = message.get("content")

        if not isinstance(content, str):
            continue

        if role == "user":
            messages.append(HumanMessage(content=content))

        elif role == "assistant":
            messages.append(AIMessage(content=content))

    return messages


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message: str, history: list | None) -> str:
    """
    Handle a user message and return a grounded response.

    The application delegates retrieval and generation to RAGPipeline.
    """

    langchain_history = convert_history(history)

    answer, sources = pipeline.answer_question(
        question=message, history=langchain_history,
    )

    source_names = []

    for document in sources:
        source = document.metadata.get(
            "source",
            "Unknown source",
        )

        source_names.append(Path(source).name)

    # Remove duplicate source names while preserving order.
    source_names = list(dict.fromkeys(source_names))

    if source_names:
        sources_markdown = "\n".join(
            f"- {source}"
            for source in source_names
        )

        answer = (
            f"{answer}\n\n"
            f"**Sources**\n"
            f"{sources_markdown}"
        )

    return answer


# ---------------------------------------------------------------------------
# Gradio interface
# ---------------------------------------------------------------------------

DESCRIPTION = """
Ask questions about David's professional experience, skills, projects,
and technical background.

Responses are generated using Retrieval-Augmented Generation (RAG)
and grounded in the project knowledge base.
"""


demo = gr.ChatInterface(
    fn=chat,
    type="messages",
    title="AI Career Assistant",
    description=DESCRIPTION,
    examples=[
        "Summarize David's professional experience.",
        "What is David's machine learning experience?",
        "How does David handle communicating technical ideas to non-technical teams?",
    ],
    textbox=gr.Textbox(
        placeholder="Ask about David's experience...",
    ),
)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch(inbrowser=True)