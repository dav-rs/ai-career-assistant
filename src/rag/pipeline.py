"""
RAG pipeline for the AI Career Assistant.

The pipeline owns:
- Vector store initialization.
- Semantic retrieval.
- Prompt construction.
- Conversation history handling.
- LLM response generation.

The module is intentionally self-contained for the MVP.
"""

from pathlib import Path
import logging

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.rag.prompts import build_messages 

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLM_MODEL = "gpt-5.6-luna"

DEFAULT_TOP_K = 7

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    The class encapsulates the dependencies required by the application so
    callers only need to provide a user question and optional conversation
    history.
    """

    def __init__(self, vector_store: Chroma,
        *,
        llm_model: str = LLM_MODEL,
        top_k: int = DEFAULT_TOP_K,
    ) -> None:
        """
        Initialize the RAG pipeline.

        Parameters
        ----------
        vector_store
            the ChromaDB object 

        llm_model
            OpenAI chat model used for response generation.

        top_k
            Number of documents retrieved for each question.
        """

        self.top_k = top_k
        # increase fetched chunks to include more project chunks
        self.overfetch_k = max(top_k * 3, 20)

        self.vector_store = vector_store
        print(f"Vectorstore Loaded with {self.vector_store._collection.count()} vectors.")

        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": self.overfetch_k})

        self.llm = ChatOpenAI(model=llm_model, temperature=0)

    def _retrieve(self, question: str, history: list | None = None) -> list[Document]:
        """
        Retrieve documents relevant to the current question.

        Recent user questions are included to improve retrieval for simple
        conversational follow-ups such as "Can you expand on that?".
        """

        recent_questions: list[str] = []

        if history:
            # Allow for up to 3 previous questions to be considered for the retrieval of context 
            recent_questions = [message.content for message in history if isinstance(message, HumanMessage)][-3:]

        retrieval_query = "\n".join([*recent_questions, question])

        docs = self.retriever.invoke(retrieval_query)

        projects = [d for d in docs if d.metadata.get("type") == "project"]
        others = [d for d in docs if d.metadata.get("type") != "project"]

        min_projects = min(2, len(projects))  # guarantee up to 2, if that many exist at all
        remaining_slots = self.top_k - min_projects

        result_docs = projects[:min_projects] + others[:remaining_slots]

        if len(result_docs) < self.top_k:
            extra_needed = self.top_k - len(result_docs)
            result_docs += projects[min_projects : min_projects + extra_needed]


        # # Debug: print retrieved chunks to console for inspection during development.
        # logger.debug("Retrieved %d chunks for query: %r", len(docs), retrieval_query)
        # for i, doc in enumerate(docs):
        #     logger.debug("[%d] source=%s type=%s | %r", i, doc.metadata.get("source"), doc.metadata.get("type"), doc.page_content[:150])

        # Debug: print retrieved chunks to console for inspection during development.
        project_count = sum(1 for d in result_docs if d.metadata.get("type") == "project")
        print(f"\n--- Retrieved {len(result_docs)} chunks for query: {retrieval_query!r} "
            f"({project_count} project chunk(s)) ---")
        for i, doc in enumerate(result_docs):
            print(f"[{i}] source={doc.metadata.get('source')} type={doc.metadata.get('type')}")
            print(f"    {doc.page_content[:500]!r}")
        print("--- end retrieved chunks ---\n")

        return result_docs[: self.top_k]

    def _format_context(self, docs: list[Document]) -> str:
        """
        Format retrieved documents with attribution metadata so the LLM can
        ground claims in specific, citable sources rather than anonymous prose.
        Only metadata that aids attribution or precision (title, type, date)
        is surfaced — skills/tools are omitted since they're already covered
        in the page content itself and would only add redundant noise.
        """
        blocks = []
        for doc in docs:
            meta = doc.metadata
            label = meta.get("title") or meta.get("source", "unknown source")
            doc_type = meta.get("type", "document")
            date = meta.get("year") or meta.get("end_date") or meta.get("date_updated")

            header = f"[{doc_type.upper()}: {label}"
            if date:
                header += f" — {date}"
            header += "]"

            blocks.append(f"{header}\n{doc.page_content}")
        return "\n\n".join(blocks)

    def answer_question(self, question: str, history: list | None = None) -> tuple[str, list[Document]]:
        """
        Generate a grounded answer to a user question.

        Parameters
        ----------
        question
            Current user question.

        history
            Previous conversation messages in LangChain message format.

        Returns
        -------
        tuple[str, list[Document]]
            Generated answer and retrieved source documents.
        """

        retrieved_docs = self._retrieve(question=question, history=history)

        context = self._format_context(retrieved_docs)

        messages = build_messages(question=question, context=context, history=history)

        response = self.llm.invoke(messages)

        return response.content, retrieved_docs

    def stream_answer(self, question: str, history: list | None = None):
        """
        Stream a grounded answer to a user question chunk-by-chunk.

        Parameters
        ----------
        question
            Current user question.
        history
            Previous conversation messages in LangChain message format.

        Yields
        -------
        str
            Incremental text chunks from the LLM model.
        
        Returns
        -------
        list[Document]
            Retrieved source documents (yielded/handled at pipeline termination).
        """
        retrieved_docs = self._retrieve(question=question, history=history)

        context = self._format_context(retrieved_docs)

        messages = build_messages(question=question, context=context, history=history)

        # Stream chunks from ChatOpenAI using LangChain's .stream()
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield ("token", chunk.content)

        yield ("sources", retrieved_docs)