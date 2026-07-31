# ADR-0004: Vector Store Persistence

**Status:** Accepted

**Date:** 2026-07-31

---

## Context

The application is deployed on Hugging Face Spaces, where local storage is ephemeral.

The knowledge base consists of a small number of documents describing professional experience. Rebuilding the vector index requires only a few seconds during application startup.

A persistence strategy is required for the vector store.

---

## Decision

Use an embedded ChromaDB instance and rebuild the vector index during application startup.

The ingestion process shall be idempotent allowing the application to safely rebuild its vector store every time a new container starts.

The persistence strategy will be revisited if the knowledge base size or deployment architecture changes.

---

## Alternatives Considered

### Embedded ChromaDB with startup indexing

Rebuild the vector store each time the application starts.

**Selected**

Simple architecture, zero infrastructure cost, and appropriate for the current knowledge base size.

---

### External persistent vector database

Store embeddings in a managed vector database or persistent volume.

**Rejected**

Provides durable storage but introduces additional infrastructure, authentication, operational cost, monitoring requirements, and deployment complexity.

The current project does not justify these trade-offs.

---

## Consequences

### Positive

- Zero infrastructure cost.
- Simple deployment.
- Minimal operational complexity.
- Deterministic startup process.
- Easy local development.

### Negative

- Small cold-start latency while rebuilding embeddings.
- Index freshness is tied to deployment.
- Not appropriate for large knowledge bases or multi-instance deployments.

---

## Revisit Criteria

This decision should be reconsidered when one or more of the following conditions are met:

- The knowledge base grows significantly.
- Multiple application instances require a shared index.
- Real-time document updates become necessary.
- Startup latency becomes unacceptable.
- Persistent storage becomes an operational requirement.