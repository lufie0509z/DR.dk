# Milestone 6: Interactive Detail Lookup

## Scope

This milestone resolves a numbered digest item back to the source story and builds a longer detail artifact.

Implemented:

- read a stored digest menu JSON
- resolve story number to the corresponding item
- generate a longer detail payload in the requested language
- write JSON and text artifacts for later Telegram delivery

Out of scope:

- Telegram bot messaging
- button actions
- automated reply handling from Telegram
- daily scheduling

## Detail strategy

The detail layer uses already stored content from the normalized snapshot and menu artifact.

Priority:

- use localized fields when the requested language is available
- otherwise fall back to source Danish fields

## What was implemented

### Lookup module

- [lookup.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/digest/lookup.py) loads a menu artifact and resolves item numbers such as `3`.

### Long-summary module

- [long_summary.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/summarize/long_summary.py) builds a detail payload and renders a ready-to-send text response.

### CLI support

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) adds:
  - `detail --menu-json <path> --number <n>`
  - optional `--language da|en|zh`

Example:

```bash
PYTHONPATH=src .venv/bin/python -m dr_digest detail \
  --menu-json var/digests/dr/2026-04-15/2026-04-15T21-41-41Z.menu.json \
  --number 3 \
  --language en
```

### Storage

- [files.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/storage/files.py) now writes:
  - `<timestamp>.detail.<number>.json`
  - `<timestamp>.detail.<number>.txt`

Default directory:

- `var/digests/dr/YYYY-MM-DD/`

## Output shape

The detail artifact contains:

- story number
- GUID
- display language
- title
- summary
- body text
- section
- published time
- source link

## Verification

Verified with:

- unit tests for menu lookup
- unit tests for detail payload rendering
- storage tests for detail artifacts
- CLI tests for the `detail` command

## Result

Milestone 6 is complete. The project can now resolve a menu number into a stored story and produce a longer detail artifact ready for future Telegram delivery.
