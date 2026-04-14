# DR Daily Digest

This project will read DR news every day, summarize the most important stories, and deliver the digest to Telegram.

We are building it in small tasks rather than finishing everything at once.

The earlier prototype code has been removed. The repository is now intentionally reset to a planning-first state so the real implementation can follow the agreed milestones cleanly.

## Project docs

- [Project structure](docs/PROJECT_STRUCTURE.md)
- [Decision log](docs/DECISIONS.md)
- [Milestone 1 summary](docs/MILESTONE_01_INGEST.md)

## Working rule

Important decisions and structural changes should be recorded in markdown under `docs/`.

## Current agreed next step

Build the DR ingest path first:

1. Fetch DR RSS reliably.
2. Normalize stories into a stable internal model.
3. Save the fetched result locally so later steps are traceable.

Telegram sending should come after the ingest and summary steps are stable.

## Current implementation status

Milestone 1 is now implemented:

- `dr-digest ingest-dr` fetches DR's RSS feed.
- The raw XML is saved under `var/raw/dr/YYYY-MM-DD/`.
- A normalized JSON snapshot is saved next to the XML file.

## Quick start

1. Create a local config file.

```bash
cp .env.example .env
```

2. Run the ingest command.

```bash
PYTHONPATH=src python3 -m dr_digest ingest-dr
```

3. Optional: print the normalized items to stdout.

```bash
PYTHONPATH=src python3 -m dr_digest ingest-dr --print-items
```
