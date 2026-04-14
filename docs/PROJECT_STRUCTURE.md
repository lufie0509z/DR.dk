# Project Structure

## Goal

Read DR news every day, identify the most important stories, summarize them, and send the digest to Telegram.

## Delivery strategy

The project will be built incrementally. Each milestone should leave the repository in a working state.

## Core flow

1. Fetch DR news input.
2. Normalize the stories into a stable internal data model.
3. Enrich stories with article-page content.
4. Translate key content into English and Chinese.
5. Select the stories to include in the daily digest.
6. Summarize the selected stories.
7. Format the summary for Telegram.
8. Send the message.
9. Persist run state and outputs for traceability.

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
  select/
    __init__.py
    ranking.py
  summarize/
    __init__.py
    formatter.py
    openai_client.py
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
  select/
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

### `select/`

- Decide which stories matter enough to include.
- Start simple: latest `N` items or a rule-based score.
- Later, this can become smarter without affecting Telegram delivery code.

### `translate/`

- Translate Danish source content into user-facing languages.
- Keep translation-specific backend logic out of ingest and summary modules.
- Produce structured bilingual fields that downstream steps can reuse.

### `summarize/`

- Convert selected stories into a concise digest.
- Support an OpenAI-based summarizer and a local fallback.
- Produce one clean digest object that downstream delivery code can reuse.

### `publish/`

- Format and send messages to Telegram.
- Contain Telegram-specific payload rules and retry logic.
- No DR parsing logic should live here.

### `storage/`

- Save raw feed snapshots, generated digests, and send-state files.
- Track whether a digest for a given day has already been sent.

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

### Milestone 4: Story selection

- Decide which items make the digest.
- Start with simple, deterministic rules.
- Save the selected set for inspection.

### Milestone 5: Summarization

- Add local summary formatting first.
- Add OpenAI summarization second.
- Save the final digest markdown to `var/digests/`.

### Milestone 6: Telegram publishing

- Add Telegram Bot API integration.
- Support one bot token and one destination chat ID.
- Record send results in `var/state/`.

### Milestone 7: Daily automation

- Wire the runtime job to `launchd`.
- Prevent duplicate sends for the same digest unless forced.
- Add logs and operational notes.

## Current repo note

The earlier notification spike has been deleted. The repository should now be treated as a clean scaffold driven by the structure above.
