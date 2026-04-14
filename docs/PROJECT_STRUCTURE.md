# Project Structure

## Goal

Read DR news every day, build a compact digest of all stories, and send it to Telegram with interactive follow-up summaries on demand.

## Delivery strategy

The project will be built incrementally. Each milestone should leave the repository in a working state.

## Core flow

1. Fetch DR news input.
2. Normalize the stories into a stable internal data model.
3. Enrich stories with article-page content.
4. Translate key content into English and Chinese.
5. Generate a short summary for each story.
6. Build a numbered daily digest from all stories.
7. Persist digest state so replies can resolve back to the correct story.
8. Handle interactive requests for longer summaries.
9. Send digest and follow-up messages through Telegram.
10. Persist run state and outputs for traceability.

## Design principles

- Keep source ingestion, summarization, and notification delivery separate.
- Prefer small, testable modules over one large script.
- Persist important artifacts such as fetched feeds, generated digests, and send status.
- Make the daily job idempotent where practical so reruns do not spam Telegram.
- Record major decisions in markdown under `docs/`.

## Target package layout

```text
docs/
  DECISIONS.md
  INTERACTIVE_DIGEST_DESIGN.md
  PROJECT_STRUCTURE.md

src/dr_digest/
  __init__.py
  cli.py
  config.py
  models.py
  ingest/
    __init__.py
    dr_rss.py
    article_fetch.py
  translate/
    __init__.py
    argos_translate.py
  digest/
    __init__.py
    short_summary.py
    menu_builder.py
    lookup.py
  summarize/
    __init__.py
    long_summary.py
  publish/
    __init__.py
    telegram.py
  storage/
    __init__.py
    files.py
    state.py
  runtime/
    __init__.py
    digest_job.py

tests/
  ingest/
  translate/
  digest/
  summarize/
  publish/
  storage/
  runtime/

scripts/
  run_daily_digest.sh

ops/
  com.xinyi.drdk.digest.plist

var/
  raw/
  digests/
  state/
  logs/
```

## Responsibility of each area

### `ingest/`

- Read DR RSS feeds.
- Optionally fetch article pages for extra context.
- Return normalized `NewsItem` objects only.
- Do not summarize or send notifications here.

### `translate/`

- Translate Danish source content into user-facing languages.
- Keep translation-specific backend logic out of ingest and summary modules.
- Produce structured bilingual fields that downstream steps can reuse.

### `digest/`

- Generate short summaries for every story.
- Build numbered digest messages and batch them when needed.
- Persist lookup data so a user reply can map back to the chosen story.

### `summarize/`

- Generate longer summaries for a specific chosen story.
- Keep long-summary logic separate from the short daily digest layer.

### `publish/`

- Send digest messages and follow-up detail messages to Telegram.
- Contain Telegram-specific message formatting, batching, and interaction logic.
- No DR parsing logic should live here.

### `storage/`

- Save raw feed snapshots, generated digests, and interactive state files.
- Track whether a digest for a given day has already been sent.
- Store story-number mappings for follow-up requests.

### `runtime/`

- Orchestrate the end-to-end daily job.
- Handle scheduling entrypoints, logging, and top-level error handling.

## Planned milestones

### Milestone 1: DR ingest

- Fetch DR RSS.
- Parse stories into internal models.
- Save a raw snapshot to `var/raw/`.
- Add unit tests for feed parsing.

### Milestone 2: Enriched ingest

- Fetch linked article pages.
- Extract article metadata and body text.
- Save raw article HTML plus enriched item fields.

### Milestone 3: Translation

- Translate items into English and Chinese.
- Save bilingual output inside the normalized snapshot.
- Keep translation optional and limitable.

### Milestone 4: Short summaries for all stories

- Generate one-sentence summaries for every story.
- Save the short-summary result in a digest-oriented artifact.

### Milestone 5: Daily digest assembly

- Build a numbered digest from all stories.
- Add batching rules for long daily lists.
- Save item-number mappings for lookup.

### Milestone 6: Interactive detail summaries

- Generate longer summaries for a single requested story.
- Resolve user replies like `3` back to stored digest items.

### Milestone 7: Telegram interaction layer

- Add Telegram Bot API integration.
- Send the numbered digest.
- Support follow-up replies or button-based requests for detail.

### Milestone 8: Daily automation

- Wire the runtime job to `launchd`.
- Prevent duplicate sends unless forced.
- Keep per-day interactive digest state available.

## Current repo note

The earlier notification spike has been deleted. The repository should now be treated as a clean scaffold driven by the structure above.
