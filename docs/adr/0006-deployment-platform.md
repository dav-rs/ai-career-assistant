# ADR-0006: Deployment Platform

**Status:** Accepted

**Date:** 2026-07-31

---

## Context

The application requires a public deployment platform that enables recruiters and hiring managers to interact with the chatbot without local setup.

The deployment platform should support containerized Python applications, integrate well with Gradio, and minimize operational overhead.

---

## Decision

Deploy the application using **Hugging Face Spaces**.

The application will be packaged as a Docker container and deployed through an automated build process.

---

## Alternatives Considered

### Hugging Face Spaces

Managed hosting platform for AI applications.

**Selected**

Provides native Gradio support, simple deployment, and a public URL suitable for demonstrations.

---

### Render

General-purpose cloud platform.

**Rejected**

Capable platform but provides no meaningful advantage for the current project while requiring additional deployment configuration.

---

### Railway

Cloud application platform.

**Rejected**

Simple deployment experience but less aligned with AI-focused application hosting.

---

### Azure App Service / Google Cloud Run

Production cloud platforms.

**Rejected**

Provide greater flexibility but introduce unnecessary operational complexity for the MVP.

---

## Consequences

### Positive

- Simple deployment.
- Public application URL.
- Native Gradio integration.
- Low operational overhead.
- Supports Docker-based deployment.

### Negative

- Platform-specific resource limits.
- Ephemeral local storage.
- Less deployment flexibility than general cloud platforms.

---

## Revisit Criteria

This decision should be reconsidered when one or more of the following conditions are met:

- Higher availability becomes necessary.
- Infrastructure customization is required.
- Application traffic exceeds platform limits.
- Enterprise deployment becomes a requirement.