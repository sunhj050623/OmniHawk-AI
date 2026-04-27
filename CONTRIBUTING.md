# Contributing to OpenHawk

Thanks for contributing.

This project is evolving toward an AI intelligence operating system. Contributions are welcome in data sources, ingestion quality, dedupe, UI, documentation, and developer tooling.

## What We Accept

- New source connectors (official blogs, docs, release feeds, reports)
- Bug fixes and reliability improvements
- Data normalization and dedupe improvements
- Documentation improvements
- UI/UX refinements for panel/progress pages
- CI and release automation improvements

## Local Setup

1. Clone repository.
2. Install dependencies (recommended via `uv`):
   - `uv sync`
3. Start with Docker:
   - `cd docker`
   - `docker compose up -d --build`
4. Open panel:
   - `http://127.0.0.1:18080`

## Branch & Commit Convention

- Branch names:
  - `feat/<short-topic>`
  - `fix/<short-topic>`
  - `docs/<short-topic>`
- Keep commits focused and atomic.
- Do not bundle unrelated changes in one PR.

## Pull Request Checklist

Before opening a PR, ensure:

- Code compiles/runs locally.
- Changes are scoped to one concern.
- Docs are updated if behavior/config changed.
- New connector changes include sample output and dedupe rationale.
- No secrets/keys/tokens are committed.

## Source Connector Contribution Rules

For source-related PRs, include:

- Source type and ownership (official doc/blog/media/research).
- Expected update cadence (hourly/daily/weekly).
- Example event mapping to schema fields.
- Dedupe key strategy (which fields and why).
- Failure handling strategy (timeouts, malformed payloads, retries).

## Quality Bar

PRs should preserve or improve:

- Freshness
- Deduplication
- Traceability
- Parsing robustness

## Security and Compliance

- Do not bypass robots/terms in ways that violate source policies.
- Do not exfiltrate private data.
- Keep credentials in env/config only; never commit secrets.

## Getting Help

- Open an issue with reproducible steps and logs.
- For feature proposals, include problem statement, scope, and expected impact.

