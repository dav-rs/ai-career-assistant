# ADR-0005: Embedding Model

**Status:** Accepted

**Date:** 2026-08-01

---

## Context

The application requires an embedding model to convert documents and user queries into vector representations for semantic retrieval.

The selected model should provide high retrieval quality, simple integration, predictable operational cost, and minimal infrastructure overhead.

---

## Decision

Use **OpenAI's text-embedding-3-small** model.

The model provides high-quality semantic embeddings, native API integration, and eliminates the need to manage embedding infrastructure during the MVP.

---

## Alternatives Considered

### OpenAI text-embedding-3-small

Managed embedding service.

**Selected**

Provides strong retrieval quality, simple integration, and low operational complexity.

---

### OpenAI text-embedding-3-large

Higher-quality managed embeddings.

**Rejected**

Improved retrieval quality does not justify the additional cost for the current corpus size.

---

### Open-source embedding models

Examples include BAAI BGE and Sentence Transformers.

**Rejected**

Avoids API costs but introduces model hosting, dependency management, and additional infrastructure that are unnecessary for the MVP.

---

## Consequences

### Positive

- High retrieval quality.
- Minimal infrastructure.
- Native Python integration.
- Consistent embeddings across environments.
- Easy to maintain.

### Negative

- External API dependency.
- Usage-based pricing.
- Internet connectivity required.

---

## Revisit Criteria

This decision should be reconsidered when one or more of the following conditions are met:

- API costs become significant.
- Offline inference becomes a requirement.
- Data privacy requires self-hosted models.
- Retrieval quality needs exceed the selected model.