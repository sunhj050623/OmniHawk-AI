# OpenHawk Roadmap (AI Intelligence OS)

This roadmap positions OpenHawk as an AI intelligence operating system rather than a simple news crawler.


For a detailed Chinese expansion plan, see `docs/EXPANSION-PLAN-ZH.md`.

## Product Goal

Build a trustworthy, evidence-backed intelligence pipeline for AI:

- AI papers and research signals
- Model/company technical releases
- AI finance and market signals
- AI policy and compliance updates
- AI safety incidents and risk signals

## Guiding Principles

1. Source-first reliability: prioritize official and primary sources.
2. Event-centric architecture: normalize all inputs into structured events.
3. Traceability by default: every event must include source URL and evidence.
4. Noise suppression: dedupe and novelty scoring are mandatory.
5. Global + local coverage: support CN and global ecosystems equally.

## 0-30 Days (Foundation)

- Stabilize event schema v1 in code and docs.
- Implement source tiering: official docs/blogs > reputable media > social.
- Enforce recency defaults for progress feeds (for example 90 days).
- Improve dedupe with rule-based key + semantic similarity fallback.
- Add mandatory fields validation in ingestion pipeline.
- Add contribution guidelines and connector SDK docs.

Exit Criteria:

- 40+ high-quality sources enabled.
- Duplicate push rate under 5%.
- 95% of pushed events contain valid source links.

## 31-60 Days (Coverage Expansion)

- Add AI finance module:
  - earnings-call AI mentions
  - capex / gpu spend signals
  - M&A and funding events
- Add AI industry reports module:
  - major consulting/research reports
  - trend extraction and stance comparison
- Add entity graph extraction: org, model, product, region, domain.
- Add topic watchlists and per-topic weekly digest.

Exit Criteria:

- 80+ sources total.
- Structured finance/report events in production.
- Weekly digest generation for at least 5 core topics.

## 61-90 Days (Decision Intelligence)

- Add policy and regulation module (CN, US, EU, key APAC).
- Add safety/incident module with severity labels.
- Add impact scoring and confidence scoring.
- Add analyst views:
  - what changed this week
  - disagreement/consensus view across sources
- Publish data quality dashboard and monthly transparency report.

Exit Criteria:

- 120+ curated sources.
- Severity and confidence available for major event types.
- Public quality metrics page available.

## Core Metrics

Track these continuously:

- Coverage: key-source hit rate by category.
- Freshness: median lag from publish time to ingestion.
- Quality: duplicate rate, invalid-link rate, parse-failure rate.
- Insight quality: human rating for summary usefulness.
- Delivery quality: push CTR / open rate / unsubscribe rate.

## Backlog Themes (After 90 Days)

- Multi-language summarization quality improvements.
- Historical trend backtesting for model-release impact.
- Open data snapshot export (daily/weekly).
- Plugin ecosystem for third-party connectors.
- Team collaboration features (annotation, triage, assignment).



