# Milestone 5: Daily Digest Assembly

## Scope

This milestone turns the short summaries into a numbered daily digest artifact.

Implemented:

- build a numbered menu from all stories
- choose display text in the configured digest language
- batch the digest into message-sized chunks
- save the item-number mapping for later reply lookup

Out of scope:

- Telegram delivery
- button interactions
- on-demand long summaries
- daily scheduling

## Digest strategy

The daily digest uses:

- stable numbering based on item order
- localized display text when translations are available
- fallback to Danish source text when a translation is missing
- fixed-size batching for long lists

## What was implemented

### Menu builder

- [menu_builder.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/digest/menu_builder.py) builds:
  - numbered digest entries
  - localized display fields
  - batched menu text payloads

### CLI integration

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) now creates the daily digest artifact after short summaries are generated.
- the command output now includes:
  - `menu_json_path`
  - `menu_batch_dir`
  - `menu_batch_count`

### Storage

- [files.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/storage/files.py) now writes:
  - `<timestamp>.menu.json`
  - `<timestamp>.menu/01.txt`, `02.txt`, ...

Default directory:

- `var/digests/dr/YYYY-MM-DD/`

### Configuration

- [.env.example](/Users/xinyi/Desktop/code/DR.dk/.env.example) now includes:
  - `DIGEST_LANGUAGE`
  - `DIGEST_BATCH_SIZE`

## Output shape

The digest menu artifact contains:

- numbered entry list
- GUID mapping
- display language
- per-batch item ranges
- rendered text for each batch

This prepares the pipeline for Telegram reply lookup in the next milestone.

## Verification

Verified with:

- unit tests for localized menu building and batching
- storage tests for persisted menu files
- CLI tests for menu artifact paths
- full test suite and bytecode compilation
- live end-to-end run against DR data

## Result

Milestone 5 is complete. The pipeline can now assemble a numbered daily digest from all stories and persist the menu structure needed for later interactive lookup.
