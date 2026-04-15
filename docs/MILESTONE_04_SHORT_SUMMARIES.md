# Milestone 4: Short Summaries For All Stories

## Scope

This milestone adds a short-summary layer for every story.

Implemented:

- generate a one-sentence summary for every story
- generate localized short summaries when translations exist
- save a digest-oriented artifact for later interactive menu building

Out of scope:

- Telegram interaction
- long on-demand summaries
- message batching
- daily scheduling

## Summary strategy

Short summaries are generated with a local heuristic:

1. use the existing article summary if available
2. otherwise use the first sentence of the article body
3. otherwise fall back to a title-based sentence

This keeps the milestone deterministic, cheap, and testable.

## What was implemented

### Digest module

- [short_summary.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/digest/short_summary.py) generates short summaries for:
  - source Danish content
  - English translations
  - Chinese translations

### Data model extension

- [models.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/models.py) now stores `short_summary` on:
  - `NewsItem`
  - `LocalizedNewsItem`

### Storage

- [files.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/storage/files.py) now writes a digest-oriented artifact:
  - `<timestamp>.short.json`

Default directory:

- `var/digests/dr/YYYY-MM-DD/`

### CLI integration

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) now generates short summaries automatically during the ingest pipeline
- the command output now includes:
  - `short_summary_count`
  - `short_digest_path`

## Output shape

The new short-digest artifact contains:

- item number
- title
- link
- section
- short summary
- translated title and translated short summary when available

## Verification

Verified with:

- unit tests for short-summary heuristics
- storage tests for the digest artifact
- CLI tests for summary counts and digest output
- full test suite and bytecode compilation

## Result

Milestone 4 is complete. The pipeline can now produce one-sentence summaries for all stories and save a digest-oriented artifact for the next milestone.
