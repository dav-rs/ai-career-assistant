from pathlib import Path

from ingestion.ingestion import ensure_vector_store 
from rag.pipeline import RAGPipeline

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "knowledge_base"
VECTOR_STORE_PATH = PROJECT_ROOT / "data" / "vector_db"

TOP_K = 4

vector_store = ensure_vector_store(data_dir=RAW_DATA_PATH, vector_store_path=VECTOR_STORE_PATH)


# ---------------------------------------------------------------------------
# Pipeline initialization
# ---------------------------------------------------------------------------

pipeline = RAGPipeline(vector_store=vector_store, top_k=TOP_K)

answer, sources = pipeline.answer_question(
    "Tell me about the candidate's machine learning experience."
)

print(answer)
print(sources)