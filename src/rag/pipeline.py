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

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.rag.prompts import build_messages 

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLM_MODEL = "gpt-5.6-luna"

DEFAULT_TOP_K = 3


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

        self.vector_store = vector_store
        print(f"Vectorstore Loaded with {self.vector_store._collection.count()} vectors.")

        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})

        self.llm = ChatOpenAI(model=llm_model, temperature=0)

    def _retrieve(self, question: str, history: list | None = None) -> list[Document]:
        """
        Retrieve documents relevant to the current question.

        Recent user questions are included to improve retrieval for simple
        conversational follow-ups such as "Can you expand on that?".
        """

        recent_questions: list[str] = []

        if history:
            # Allow for up to 2 previous questions to be considered for the retrieval of context 
            recent_questions = [message.content for message in history if isinstance(message, HumanMessage)][-2:]

        retrieval_query = "\n".join([*recent_questions, question])

        return self.retriever.invoke(retrieval_query)

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

        context = "\n\n".join(document.page_content for document in retrieved_docs)

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

        context = "\n\n".join(document.page_content for document in retrieved_docs)

        messages = build_messages(question=question, context=context, history=history)

        # Stream chunks from ChatOpenAI using LangChain's .stream()
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield ("token", chunk.content)

        yield ("sources", retrieved_docs)