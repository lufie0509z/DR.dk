# DR Daily Digest

This project will read DR news every day, build a compact digest of all stories, and deliver it to Telegram with on-demand long summaries for the stories the user asks about.

We are building it in small tasks rather than finishing everything at once.

The earlier prototype code has been removed. The repository is now intentionally reset to a planning-first state so the real implementation can follow the agreed milestones cleanly.

## Project docs

- [Project structure](docs/PROJECT_STRUCTURE.md)
- [Decision log](docs/DECISIONS.md)
- [Interactive digest design](docs/INTERACTIVE_DIGEST_DESIGN.md)
- [Milestone 1 summary](docs/MILESTONE_01_INGEST.md)
- [Milestone 2 summary](docs/MILESTONE_02_ENRICHED_INGEST.md)
- [Milestone 3 summary](docs/MILESTONE_03_TRANSLATION.md)
- [Milestone 4 summary](docs/MILESTONE_04_SHORT_SUMMARIES.md)
- [Milestone 5 summary](docs/MILESTONE_05_DAILY_DIGEST_ASSEMBLY.md)

## Working rule

Important decisions and structural changes should be recorded in markdown under `docs/`.

## Current implementation status

Milestone 1, Milestone 2, Milestone 3, Milestone 4, and Milestone 5 are now implemented:

- `dr-digest ingest-dr` fetches DR's RSS feed.
- The raw XML is saved under `var/raw/dr/YYYY-MM-DD/`.
- A normalized JSON snapshot is saved next to the XML file.
- Optional article enrichment fetches DR article pages and stores article HTML plus enriched fields such as section, summary, body text, and authors.
- Optional translation adds English and Chinese translations to each saved item with Argos Translate.
- The pipeline now generates one-sentence short summaries for all stories and writes a digest-oriented artifact under `var/digests/`.
- The pipeline now assembles a numbered daily digest menu and writes batch-ready menu files for later Telegram delivery.

The next product direction is an interactive digest:

- send a numbered list of all stories for the day
- include a one-sentence summary for each story
- let the user request a longer summary by replying with the story number

## Quick start

1. Create a local virtual environment and install project dependencies.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

2. Create a local config file.

```bash
cp .env.example .env
```

3. Run the ingest command.

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest ingest-dr
```

4. Optional: enrich article pages for the first 5 items.

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest ingest-dr --enrich-articles
```

5. Optional: translate the first 5 items to English and Chinese.

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest ingest-dr --translate
```

6. Optional: enrich and translate in one run.

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest ingest-dr --enrich-articles --translate
```

7. Optional: print the normalized items to stdout.

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest ingest-dr --print-items
```

Translation with Argos Translate will download language models on the first run and then run locally.
On this macOS/Homebrew setup, the project should be run from the local virtual environment rather than the system Python.
By default, `DR_TRANSLATION_COUNT=0` means "translate all items".
