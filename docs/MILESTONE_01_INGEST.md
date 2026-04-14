# Milestone 1: DR Ingest

## Scope

This milestone implements only the first part of the pipeline:

- fetch DR news from RSS
- normalize the feed into internal data models
- save the fetched result locally for later processing

Out of scope:

- story selection
- summarization
- Telegram delivery
- scheduling

## Source

- Default feed: `https://www.dr.dk/nyheder/service/feeds/senestenyt`
- Source type: RSS 2.0
- Verified on: April 14, 2026

## What was implemented

### Configuration

- [config.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/config.py) loads `.env` values for the DR feed URL, timeout, item limit, and raw storage directory.
- [.env.example](/Users/xinyi/Desktop/code/DR.dk/.env.example) documents the minimal ingest configuration.

### Ingest

- [dr_rss.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/ingest/dr_rss.py) fetches the RSS feed and parses:
  - channel title
  - channel description
  - item title
  - item link
  - item guid
  - item publish time
  - optional media image URL

### Internal models

- [models.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/models.py) defines:
  - `NewsItem`
  - `FeedSnapshot`
  - `IngestArtifacts`

### Storage

- [files.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/storage/files.py) saves two files for each ingest run:
  - raw RSS XML: `<timestamp>.feed.xml`
  - normalized JSON snapshot: `<timestamp>.items.json`

Storage path:

- `var/raw/dr/YYYY-MM-DD/`

### CLI

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) adds the command:

```bash
PYTHONPATH=src python3 -m dr_digest ingest-dr
```

Useful options:

- `--feed-url`
- `--max-items`
- `--print-items`

## Output example

Example artifacts created during verification:

- [2026-04-14T13-38-20Z.feed.xml](/Users/xinyi/Desktop/code/DR.dk/var/raw/dr/2026-04-14/2026-04-14T13-38-20Z.feed.xml)
- [2026-04-14T13-38-20Z.items.json](/Users/xinyi/Desktop/code/DR.dk/var/raw/dr/2026-04-14/2026-04-14T13-38-20Z.items.json)

## Verification

The milestone was verified with:

- unit tests for RSS parsing, storage, and CLI execution
- a fixture-based ingest run
- a live ingest run against DR's RSS feed

Commands used:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 -m compileall src
PYTHONPATH=src python3 -m dr_digest ingest-dr --max-items 5
```

## Result

Milestone 1 is complete. The repository can now ingest DR news reliably and persist raw plus normalized artifacts for the next milestone.
