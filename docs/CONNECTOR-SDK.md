# Connector SDK Specification

This document defines a stable connector interface for AI intelligence ingestion.

## Goals

- Make source onboarding fast and predictable.
- Keep connector code small and testable.
- Guarantee normalized output for downstream dedupe and enrichment.

## Connector Contract

Each connector should expose:

- `id`: stable source identifier (for example `openai_news`)
- `kind`: source kind (`official_site`, `official_blog`, `rss`, `report`, `media`)
- `org`: organization (for example `OpenAI`)
- `region`: region hint (`cn`, `global`, `us`, `eu`, ...)
- `fetch() -> list[RawEvent]`

## RawEvent (Connector Output)

Required fields:

- `title`
- `url`
- `published_at` (ISO 8601)
- `source_id`
- `source_name`

Recommended fields:

- `summary`
- `tags`
- `event_type` (`release`, `update`, `report`, `benchmark`, `policy`, `safety`)
- `org`
- `region`

## Normalized Event Schema (Pipeline Output)

Canonical fields:

- `event_id` (stable hash)
- `event_type`
- `org`
- `entities` (models/products/orgs)
- `title`
- `summary`
- `url`
- `published_at`
- `fetched_at`
- `source_id`
- `source_name`
- `source_tier`
- `region`
- `tags`
- `confidence`
- `novelty_score`
- `impact_score`
- `evidence[]`

## Dedupe Strategy

Use two layers:

1. Deterministic key:
   - primary: normalized URL
   - fallback: hash(title + org + date bucket)
2. Semantic near-duplicate:
   - compare title/summary embeddings
   - merge when similarity is above threshold

When merged, keep:

- earliest `published_at`
- highest `source_tier`
- union of tags/evidence

## Error Handling

Connector fetch should be resilient:

- timeout with retry (bounded)
- skip malformed records, continue batch
- emit parse-failure metrics

Do not raise hard failure for one bad item unless the whole source is unavailable.

## Minimal Python Skeleton

```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SourceConnector:
    id: str
    kind: str
    org: str
    region: str

    def fetch(self) -> List[Dict[str, Any]]:
        raise NotImplementedError


class OpenAINewsConnector(SourceConnector):
    def __init__(self) -> None:
        super().__init__(
            id="openai_news",
            kind="official_blog",
            org="OpenAI",
            region="global",
        )

    def fetch(self) -> List[Dict[str, Any]]:
        # 1) request source
        # 2) parse items
        # 3) return normalized raw events
        return []
```

## Acceptance Checklist for New Connector

- Stable `source_id` and owner metadata.
- At least 3 sample events parsed successfully.
- Event type mapping documented.
- Dedupe key strategy documented.
- Error handling tested on malformed payload.

## Testing Recommendations

- Snapshot test for parser output.
- Contract test for required fields.
- Regression test for one known historical item.
