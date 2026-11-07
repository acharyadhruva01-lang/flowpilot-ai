# FlowPilot AI ✦

A portfolio-ready, local-first **GitHub → LLM → human approval → Slack** workflow app. Built with FastAPI, a responsive HTML/CSS/JS dashboard, SQLite, and either **Ollama (default)** or **OpenAI (optional)**.

> This is a working MVP, not a production multi-tenant SaaS. Do not deploy it publicly with a shared approval secret or private GitHub token. The demo is intended for local use and trusted environments.

## Features

- Retrieve real open issues from a GitHub repository (excludes pull requests)
- Analyze issues with an LLM; generate a report and editable Slack draft
- Default to **Ollama**; optionally switch to OpenAI using your own API key
- Display source issue links, run history, and posting status
- **Require explicit user confirmation and an approval secret** before posting to Slack
- Store analysis history in SQLite
- REST API, Dockerfile, tests, environment-variable configuration

## Quick start (Windows / macOS / Linux)

1. Install **Python 3.11+**, **Git**, and **Ollama** from https://ollama.com/download.
2. In a terminal run `ollama pull llama3.2`. Ensure Ollama is running (on some systems run `ollama serve` in another terminal).
3. Download/extract this project and open a terminal inside `flowpilot-ai`.
4. Copy `.env.example` to `.env`:
   - macOS/Linux: `cp .env.example .env`
   - Windows PowerShell: `Copy-Item .env.example .env`
5. Create a virtual environment:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows PowerShell: `py -m venv .venv; .\.venv\Scripts\Activate.ps1`
6. Install packages: `python -m pip install -r requirements.txt`
7. Start the app: `uvicorn app.main:app --reload`
8. Open **http://localhost:8000**. Try `fastapi/fastapi` or another public repo with open issues.

**Note:** Initial model downloads may be several GB; Ollama needs adequate RAM. The first inference can be slow. This app does not ship with a model or paid API credits.

## Optional OpenAI mode

Edit `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Restart the backend. OpenAI API usage is billed separately from ChatGPT subscriptions. **Do not commit `.env`**.

## Optional Slack posting

1. Create a Slack app with an **Incoming Webhook** in your own workspace/channel: https://api.slack.com/messaging/webhooks
2. Add `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...` to `.env`.
3. Set `APP_SECRET` to a long random string (e.g., `python -c "import secrets; print(secrets.token_urlsafe(32))"`).
4. Restart the app. Analyze a repo, **review/edit the draft**, enter your approval secret in the UI, and click **Approve & post**. A confirmation dialog appears before sending.

Posting is off until both environment values are configured. For a local demo, you can leave Slack unconfigured and demonstrate draft generation.

## Optional GitHub token

Public GitHub issues work without a token, subject to rate limits. Set `GITHUB_TOKEN` in `.env` for higher limits. Private repositories are blocked by default, even if a token is provided. Never use a token with more privileges than necessary. GitHub issue text is untrusted; the model is explicitly instructed not to obey instructions embedded in issues.

## Tests

```bash
python -m pytest -q
```

## Docker

For OpenAI mode, `docker compose up --build` works with a populated `.env`. For Ollama running on the host, set `OLLAMA_BASE_URL=http://host.docker.internal:11434` in `.env`; ensure Ollama listens on an address reachable from the container. Then `docker compose up --build`. Visit http://localhost:8000.

## Architecture

```text
Browser dashboard
   | POST /api/analyze
FastAPI → GitHub REST API → Open issues
   |                         |
   +────── Ollama / OpenAI ←─+
   |        JSON report + Slack draft
SQLite run history
   |
Browser review + explicit approval
   | POST /api/runs/{id}/post (secret required)
Slack incoming webhook (optional)
```

## API

- `GET /api/health` — backend/model mode
- `GET /api/runs` — recent runs
- `POST /api/analyze` — `{ "repo": "owner/repo", "focus": "...", "max_issues": 10 }`
- `POST /api/runs/{id}/post` — `{ "draft": "..." }` with `X-App-Secret` header
- `GET /docs` — interactive FastAPI API documentation

## Scope, limitations, and next steps

- Current MVP is **single-user/local-first**, not multi-user authenticated; use only in a trusted environment. SQLite stores drafts, which may include repository data. The approval secret is sent only to your local backend; use HTTPS if ever deployed remotely.
- LLM outputs can be inaccurate. Check linked GitHub issues before sharing. No guarantee that model follows instructions perfectly.
- Open issues are sampled by recent update, up to 50, and not automatically prioritized by labels. API rate limits apply.
- A failed Slack response does not guarantee the message was not delivered; check the channel before retrying.
- Suggested production improvements: OAuth, per-user auth, encrypted secrets, webhook verification, durable job queue, idempotency, observability, and automated LLM evaluation.

## Interview walkthrough

1. Show GitHub issues retrieved from a real public repository.
2. Explain the untrusted-data boundary between issue content and system instructions.
3. Compare Ollama local inference with optional hosted OpenAI inference.
4. Show a saved report and its linked source issues.
5. Explain why Slack posting requires explicit approval and a secret.
6. Run the test suite and discuss production hardening.

## Resume wording (only after you run, test, and understand it)

**FlowPilot AI — LLM-Powered GitHub Workflow Assistant** | Python, FastAPI, Ollama, OpenAI API, SQLite, GitHub REST API

- Built a full-stack workflow assistant that retrieves GitHub issues and generates actionable reports and editable Slack updates using local or hosted LLMs.
- Implemented a human-approval gate for Slack posting, persistent run history, configurable model providers, and automated API tests.

**Be accurate:** The MVP does not use LangGraph, Next.js, PostgreSQL, OAuth, or autonomous scheduling. Do not list those as implemented.
