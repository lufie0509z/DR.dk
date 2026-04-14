# Milestone 3: Automatic English and Chinese Translation

## Scope

This milestone adds automatic translation to the ingest pipeline.

Implemented:

- translate Danish DR content into English
- translate Danish DR content into Simplified Chinese
- save translations directly in the normalized item snapshot

Out of scope:

- story ranking
- digest summarization
- Telegram delivery
- scheduling

## Translation strategy

Translation is implemented as an explicit pipeline stage after ingest and optional article enrichment.

Source fields translated:

- title
- section
- section path
- summary
- body text

## What was implemented

### Translation module

- [argos_translate.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/translate/argos_translate.py) adds Argos Translate-based translation.
- The translator produces two language variants for each item:
  - `en`
  - `zh`
- The first run installs the required language models locally.

### Data model extension

- [models.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/models.py) now stores bilingual translations on each `NewsItem`.

### CLI support

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) adds:
  - `--translate`
  - `--translation-limit`

Example:

```bash
PYTHONPATH=src python3 -m dr_digest ingest-dr --enrich-articles --translate --article-limit 2 --translation-limit 2
```

### Configuration

- [.env.example](/Users/xinyi/Desktop/code/DR.dk/.env.example) now includes:
  - `DR_TRANSLATION_COUNT`
  - `ARGOS_PACKAGES_DIR`

### Local model storage

Argos model files are stored locally under the configured packages directory.

Default:

- `var/argos/packages`

## Output shape

Each translated item now contains:

- `translations.en`
- `translations.zh`

The translations are saved in the same `.items.json` snapshot as the source content.

## Verification

Verified with:

- unit tests for Argos translation behavior and snapshot updates
- CLI tests for translation reporting
- full test suite and bytecode compilation

## Result

Milestone 3 is complete. The pipeline can now ingest DR news, optionally enrich article content, and automatically produce English and Chinese translations for downstream use without a paid API.
