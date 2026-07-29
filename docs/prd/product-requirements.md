# Product Requirements Document (PRD)

## 1. Executive Summary

### Project

**AI Career Assistant**

### Summary

An AI-powered career assistant that enables recruiters, hiring managers, and technical interviewers to explore professional experience through natural language conversations. The application uses Retrieval-Augmented Generation (RAG) to provide evidence-grounded responses while demonstrating production-oriented AI engineering practices.

---

## 2. Problem Statement

Traditional CVs present information as static, linear documents.

As a result:

- Practical AI engineering capabilities are not easily demonstrated through a CV alone.
- Technical experience is difficult to explore interactively.
- Recruiters often require multiple follow-up conversations.
- Project context and engineering decisions are difficult to communicate.

---

## 3. Goals

- Enable natural language interaction.
- Generate evidence-grounded responses.
- Maintain low response latency.
- Build a modular and maintainable architecture.
- Demonstrate production-quality AI engineering practices.

---

## 4. Target Users

### Primary Users

- Technical Recruiters
- Hiring Managers

### Secondary Users

- Senior Software Engineers
- AI/ML Engineers
- Data Scientists
- Engineering Managers

---

## 5. User Stories

- As a recruiter, I want to understand the candidate's experience without reading multiple documents.
- As a hiring manager, I want to explore projects through follow-up questions.
- As a technical interviewer, I want to assess depth across AI, ML, software engineering, and MLOps topics.

---

## 6. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-001 | Answer questions using the project knowledge base. |
| FR-002 | Retrieve semantically relevant context before generation. |
| FR-003 | Generate responses grounded in retrieved documents. |
| FR-004 | Display supporting source references with each response. |
| FR-005 | Support conversational follow-up questions. |

---

## 7. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Performance | Low response latency. |
| Reliability | Consistent system behavior. |
| Maintainability | Modular architecture with clear separation of concerns. |
| Reproducibility | Local environment can be reproduced from source control. |
| Observability | Log key application events and errors. |
| Testability | Components can be independently tested. |
| Security | Secrets managed outside source control. |
| Cost | Minimize operational cost while maintaining quality. |

---

## 8. Constraints

- Public professional knowledge only.
- Single-user MVP.
- No authentication.
- No model fine-tuning.
- Cloud-hosted LLM.
- Budget-conscious deployment.

---

## 9. Success Metrics

### Product

- Accurate, grounded responses.
- Useful recruiter interactions.
- Low hallucination rate.

### Engineering

- Reproducible local setup.
- Modular codebase.
- Automated quality checks in later milestones.
- Reproducible deployment.

---

## 10. Risks

| Risk | Mitigation |
|------|------------|
| Hallucinated responses | Ground responses using retrieval and citations. |
| Poor retrieval quality | Evaluate and improve chunking and retrieval strategies. |
| Outdated knowledge base | Maintain versioned source documents. |
| Increasing API costs | Monitor usage and optimize prompts and retrieval. |
| Prompt regressions | Introduce evaluation datasets in later milestones. |
| Professional interaction | Introduce guardrails through agents for acceptable answers. |

---

## 11. Future Scope

- Hybrid search.
- RAG evaluation framework.
- Conversation memory.
- User feedback collection.
- CI/CD pipeline.
- Monitoring and observability.
- Additional knowledge sources (GitHub repositories, technical blog posts, presentations).

---

## 12. AI System Boundaries

The assistant shall:

- Answer questions only from the curated knowledge base.
- Explicitly acknowledge when sufficient evidence is unavailable.
- Prioritize retrieved evidence over model prior knowledge.
- Reference supporting source documents whenever possible.
- Avoid speculation or unsupported claims.
- Handle conflicting information by communicating uncertainty rather than inventing an answer.