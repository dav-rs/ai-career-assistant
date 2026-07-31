# ADR-0002: User Interface Framework

**Status:** Accepted

**Date:** 2026-07-31

---

## Context

The project requires a lightweight web interface that enables recruiters and hiring managers to interact with the AI assistant.

The interface should prioritize rapid development, simple deployment, and seamless integration with Python-based AI workflows.

---

## Decision

Use **Gradio** as the primary user interface framework.

Gradio provides a lightweight interface for conversational AI applications while requiring minimal frontend development.

---

## Alternatives Considered

### Streamlit

Provides a rich Python web framework.

**Rejected**

Better suited to dashboards than conversational interfaces. Offers limited benefit for this use case.

---

### React frontend with FastAPI backend

Provides maximum flexibility.

**Rejected**

Introduces significant frontend complexity that is unnecessary for the MVP.

---

## Consequences

### Positive

- Rapid development.
- Native Python integration.
- Simple deployment on Hugging Face Spaces.
- Minimal frontend maintenance.
- Easy iteration.

### Negative

- Limited UI customization.
- Less suitable for highly customized production interfaces.