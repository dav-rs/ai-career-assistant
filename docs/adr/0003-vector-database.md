# ADR-0003: Vector Database

**Status:** Accepted

**Date:** 2026-07-31

---

## Context

The application requires a vector database to store document embeddings and perform semantic similarity search.

The selected solution should support local development, simple deployment, and future extensibility while keeping operational complexity low.

---

## Decision

Use **ChromaDB** as the vector database.

ChromaDB provides native Python integration, persistent local storage, and sufficient functionality for the expected project scale.

---

## Alternatives Considered

### FAISS

High-performance vector search library.

**Rejected**

Excellent retrieval performance but lacks built-in metadata management and persistence features required by the project.

---

### Pinecone

Managed vector database.

**Rejected**

Introduces additional infrastructure, authentication, operational cost, and external dependencies that are unnecessary for the MVP.

---

### Weaviate

Feature-rich managed vector database.

**Rejected**

Provides capabilities beyond current project requirements while increasing deployment complexity.

---

## Consequences

### Positive

- Simple Python integration.
- Low operational overhead.
- Suitable for local development.
- Easy migration path to managed vector databases.

### Negative

- Limited scalability compared to managed services.
- Persistence depends on deployment environment.