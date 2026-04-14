# Milestone 2: Enriched Ingest

## Scope

This milestone extends the DR ingest pipeline with article-page enrichment.

Implemented:

- fetch DR article pages from the RSS item links
- extract structured content from the article page payload
- persist enriched snapshots and raw article HTML locally

Out of scope:

- story ranking
- summarization
- Telegram delivery
- scheduling

## Source strategy

DR article enrichment is based on the structured page payload embedded in the article HTML.

Primary source inside the page:

- Next.js `__NEXT_DATA__` JSON payload

Fallback:

- meta description

## What was implemented

### Enrichment parser

- [article_fetch.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/ingest/article_fetch.py) parses:
  - section
  - section path
  - summary
  - body text
  - authors
  - article image URL
  - published time

### Data model extension

- [models.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/models.py) now stores article-level enrichment fields on each `NewsItem`.

### CLI support

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) adds:
  - `--enrich-articles`
  - `--article-limit`

Example:

```bash
PYTHONPATH=src python3 -m dr_digest ingest-dr --enrich-articles --article-limit 5
```

### Storage

The ingest output still writes:

- `<timestamp>.feed.xml`
- `<timestamp>.items.json`

When enrichment is enabled, it also writes raw article HTML files under:

- `<timestamp>.articles/`

## Why this matters

RSS headlines alone are too thin for later ranking and summarization.

With this milestone, each item can now carry:

- the article section
- a short summary
- the main body text
- author information

That makes the next milestones materially better.

## Verification

Verified with:

- parser unit tests
- storage tests
- CLI tests
- live inspection of a real DR article page on April 14, 2026

## Result

Milestone 2 is complete. The project can now ingest DR RSS and enrich selected items with article-page content for downstream selection and summarization.
