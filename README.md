# AI Career Assistant

An AI-powered career assistant built using Retrieval-Augmented Generation (RAG).

The application enables recruiters, hiring managers, and technical interviewers to explore professional experience through natural language conversations. The project demonstrates production-oriented AI engineering practices, from planning and architecture to implementation, deployment, and continuous improvement.

---

## Features

- Retrieval-Augmented Generation (RAG).
- Evidence-grounded responses.
- Semantic document retrieval.
- Modular architecture.
- Dockerized deployment.
- Public web application.

---

## System Architecture

![C4 Container Diagram](./docs/architecture/container.drawio.svg)

For detailed architecture documentation, see:

- `docs/architecture/architecture.md`

---

## Repository Structure

```text
data/
docs/
├── adr/
├── architecture/
├── prd/
└── roadmap/

scripts/
src/
tests/
.github/
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Clone the repository

```bash
git clone git@github.com:dav-rs/ai-career-assistant.git
cd ai-career-assistant
```

### Install dependencies
```bash
uv sync
```
This creates a local `.venv` and installs the exact versions pinned in `uv.lock`, so your environment matches the one used in CI and deployment. No manual virtual environment setup is required — `uv` manages it for you.

### Configure environment variables

```bash
cp .env.example .env
```
Add your API keys to `.env`.

### Run the application
```bash
uv run app.py
```
`uv run` executes the command inside the project's environment, syncing dependencies automatically if `uv.lock` has changed.

---

## Deployment

The application is containerized using Docker and deployed on Hugging Face Spaces.

> **Insert deployment URL**

---

## Engineering Practices

- GitHub Projects
- Feature branch workflow
- Pull Requests
- Conventional Commits
- Architecture Decision Records (ADRs)
- Docker
- Modular architecture
- Reproducible development environment

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/vision.md` | Project vision and guiding principles. |
| `docs/prd/product-requirements.md` | Product requirements. |
| `docs/roadmap/roadmap.md` | Project roadmap and milestones. |
| `docs/architecture/architecture.md` | System architecture. |
| `docs/adr/` | Architecture Decision Records. |

---

## Roadmap

Current progress is tracked in:

- `docs/roadmap/roadmap.md`

Development is managed through GitHub Projects and GitHub Issues.

---

## Future Improvements

- Hybrid retrieval.
- Automated evaluation.
- Conversation memory.
- Monitoring and observability.
- CI/CD pipeline.
- Multi-model support.

---

## License

This project is licensed under the MIT License.