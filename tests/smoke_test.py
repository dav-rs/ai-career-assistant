from pathlib import Path

from src.ingestion.ingestion import ensure_vector_store
from src.rag.pipeline import RAGPipeline

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "knowledge_base"
VECTOR_STORE_PATH = PROJECT_ROOT / "data" / "vector_db"


def main() -> None:
    # Exercises the bootstrap path explicitly (builds the store if missing,
    # loads it if present) — this is what actually runs on first container
    # startup, so the smoke test should cover it rather than assume a
    # pre-built store exists.
    vector_store = ensure_vector_store(
        data_dir=RAW_DATA_PATH,
        vector_store_path=VECTOR_STORE_PATH,
    )

    pipeline = RAGPipeline(vector_store=vector_store, top_k=4)

    answer, sources = pipeline.answer_question(
        "Tell me about the candidate's machine learning experience."
    )

    assert answer, "RAG pipeline returned an empty answer."
    assert sources, "RAG pipeline returned no sources."

    print("RAG smoke test passed.")


if __name__ == "__main__":
    main()