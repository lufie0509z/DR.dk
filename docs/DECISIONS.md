# Decision Log

## 2026-04-14

### Delivery channel

Telegram is the chosen notification channel for the first real version.

Reason:

- It is simpler to integrate than WhatsApp.
- It supports direct bot-based delivery well.
- It is a better fit for a small personal automation project than DingTalk.

### Execution strategy

The project will be built in small milestones instead of implementing the full pipeline at once.

Reason:

- It reduces risk.
- It makes testing and correction easier.
- It keeps the repository aligned with the actual agreed scope.

### Documentation rule

Important decisions and structural changes must be recorded in markdown files under `docs/`.

### Functional scope for the first milestone

The first milestone is DR ingest, not Telegram delivery.

Scope:

- Fetch DR RSS.
- Parse and normalize stories.
- Save fetch artifacts locally.

Out of scope for this milestone:

- Telegram sending
- Scheduling
- Advanced ranking
- Production-grade summarization

### Repository reset

The earlier email and DingTalk prototype code was deleted.

Reason:

- It no longer matched the agreed Telegram-first direction.
- It created confusion about what was current versus discarded.
- A clean scaffold is easier to evolve milestone by milestone.

### DR feed source

The ingest implementation uses `https://www.dr.dk/nyheder/service/feeds/senestenyt` as the default DR source.

Reason:

- It is DR's live RSS endpoint for the latest news feed.
- The endpoint was verified directly on April 14, 2026 and returned `HTTP/2 200`.
- It is a simpler and more stable first ingest source than scraping HTML pages.

### Ingest artifact format

The first milestone saves two files for each ingest run under `var/raw/dr/YYYY-MM-DD/`.

Files:

- `<timestamp>.feed.xml` for the raw RSS response
- `<timestamp>.items.json` for the normalized internal snapshot

Reason:

- The raw XML preserves the original source for debugging.
- The normalized JSON gives the rest of the pipeline a stable input shape.

### HTTP fetch strategy for ingest

The RSS fetcher uses Python `urllib` first and falls back to `curl` if the HTTP request fails at the client layer.

Reason:

- `urllib` keeps the default implementation small and standard-library based.
- A `curl` fallback makes the ingest more resilient when local Python networking behaves differently from the system HTTP stack.

### Article enrichment source

Milestone 2 extracts article content from DR's embedded Next.js page payload instead of scraping visible HTML paragraphs.

Reason:

- The payload contains a cleaner structured representation of the article body.
- It includes metadata such as section, authors, and images in a more stable form.
- It is less brittle than relying on CSS classes or rendered markup.

### Enriched ingest mode

Article enrichment is enabled explicitly with a CLI flag and supports a separate article fetch limit.

Reason:

- Fetching article pages is more expensive than reading the RSS feed alone.
- Explicit control keeps milestone 2 safe to run during development and testing.
- A separate limit makes it possible to enrich only the first few items before later ranking logic exists.

### Enriched artifact format

When article enrichment is enabled, raw article HTML is saved alongside the feed snapshot.

Files:

- `<timestamp>.articles/*.article.html`

Reason:

- The raw article HTML is useful for debugging parser regressions.
- Keeping article HTML next to the matching feed snapshot makes each ingest run traceable.

### Translation provider

Milestone 3 uses Argos Translate for automatic English and Chinese translation.

Reason:

- It avoids per-request API cost.
- It can run locally after the language models are downloaded.
- It fits the project's lightweight Python structure.

### Translation placement in the pipeline

Translation happens after ingest and optional article enrichment.

Reason:

- Enrichment provides better source text than RSS headlines alone.
- The translated output should reflect the final normalized source fields.
- Translation can remain optional while the rest of the pipeline is still evolving.

### Translation output format

Translations are stored inside each item under `translations.en` and `translations.zh`.

Reason:

- The translated content stays attached to its source item.
- Later ranking, summary, or Telegram formatting can choose either source or translated text without reloading separate files.
- Keeping translations in the main snapshot makes inspection easier for a non-Danish reader.

### Translation coverage default

The default translation count is `0`, which means "translate all items in the snapshot".

Reason:

- A digest configured for English or Chinese should not silently fall back to Danish for most items.
- Full translation coverage makes the menu language consistent by default.
- Explicit smaller limits can still be used during development or testing.

### Argos model strategy

The translation stage installs the required Argos language models on first use and stores them locally inside the project workspace.

Default directory:

- `var/argos/packages`

Language-pair strategy:

- `da -> en`
- `en -> zh`

Reason:

- Argos Translate supports pivot translation through installed intermediate language pairs.
- This avoids relying on a paid external translation API.
- Keeping models in the project workspace makes the setup explicit and easy to inspect.

### Python environment for local execution

The project should be run from a local virtual environment such as `.venv` instead of relying on the system Python installation.

Reason:

- The Homebrew-managed Python environment may block direct package installation.
- Argos Translate has a non-trivial dependency stack and is safer to isolate in a project-local environment.
- A local virtual environment makes the translation pipeline reproducible across runs.

### Product interaction model

The product should send a compact daily digest of all stories and let the user request longer summaries for the stories they care about.

Reason:

- It reduces the risk of hiding stories the user would want to see.
- It fits Telegram better than a one-way top-N digest.
- It makes the product interactive instead of forcing perfect selection up front.

### Digest shape

The first Telegram message should contain a numbered list of stories with one-sentence summaries.

Reason:

- A short summary is fast to scan.
- Numbering creates a simple reply-based interaction model.
- The digest remains useful even before richer Telegram UI is added.

### Follow-up detail model

Longer summaries should be generated on demand when the user replies with a story number.

Reason:

- Long summaries are only useful for the subset of stories the user cares about.
- This keeps the daily push compact.
- It avoids producing large volumes of detail the user may never read.

### Architecture change from selection to interaction

The next milestones should focus on short summaries, digest assembly, and interactive lookup instead of strict top-N story selection.

Reason:

- The new product direction depends more on digest usability than ranking precision.
- A lightweight interactive menu is a better first Telegram experience.
- Selection can still exist later as a secondary ranking aid, but it is no longer the primary user interaction.

### Short-summary strategy

Milestone 4 generates one-sentence summaries locally with a deterministic heuristic.

Priority order:

- use the article summary when available
- otherwise use the first sentence of the article body
- otherwise fall back to a title-based sentence

Reason:

- It avoids paid summarization APIs.
- It is easy to test and reason about.
- It produces usable short summaries even when enrichment is missing.

### Digest artifact format

Milestone 4 writes a digest-oriented artifact under `var/digests/` in addition to the raw snapshot under `var/raw/`.

File:

- `<timestamp>.short.json`

Reason:

- It separates digest-facing output from raw ingest storage.
- It prepares the pipeline for the next milestone, where numbered daily digest messages will be assembled.
- It gives a clean inspection point for short summaries without opening the full raw snapshot.

### Digest display language

Milestone 5 uses a configurable digest display language and falls back to Danish source text if a translation is missing.

Default:

- `DIGEST_LANGUAGE=en`

Reason:

- The user should be able to read the daily digest without reading Danish.
- A fallback to source text prevents missing entries when translation is unavailable.
- This keeps the digest usable before Telegram interaction is implemented.

### Daily digest batching strategy

The numbered digest is split into fixed-size batches for later Telegram delivery.

Default:

- `DIGEST_BATCH_SIZE=10`

Reason:

- Long one-message story lists are hard to scan.
- Telegram delivery will need chunked output for larger daily story counts.
- Fixed-size batching is simple, deterministic, and easy to test.

### Daily digest menu artifact

Milestone 5 writes a menu artifact with numbered entries and per-batch rendered text.

Files:

- `<timestamp>.menu.json`
- `<timestamp>.menu/01.txt`, `02.txt`, ...

Reason:

- The JSON artifact preserves the number-to-story mapping for later reply lookup.
- The text files give a ready-to-send representation for Telegram delivery.
- Keeping both formats makes later interaction work simpler.

### Detail lookup source of truth

Milestone 6 uses the stored menu JSON as the lookup source when resolving a reply number like `3`.

Reason:

- The menu artifact already contains stable numbering for the exact digest the user saw.
- Reply lookup must match the delivered digest, not a newly re-sorted or regenerated list.
- This keeps later Telegram interaction deterministic.

### Detail rendering strategy

The detail view should use localized fields when they exist and otherwise fall back to the original Danish source fields.

Reason:

- The requested output language should be respected when possible.
- Fallback avoids losing the ability to answer when translation is missing.
- This keeps the interaction robust while translation quality is still evolving.

### Detail artifact format

Milestone 6 writes both JSON and text artifacts for a requested story number.

Files:

- `<timestamp>.detail.<number>.json`
- `<timestamp>.detail.<number>.txt`

Reason:

- The JSON file preserves structured data for future programmatic use.
- The text file gives a ready-to-send response body for Telegram delivery.
- Writing both formats keeps the future publish layer simple.

### Telegram integration strategy

Milestone 7 uses the official Telegram Bot API over HTTPS for sending digest messages and polling for replies.

Reason:

- It is the official, supported integration path for Telegram bots.
- It fits the current CLI-first development workflow.
- It avoids introducing a server requirement before automation is implemented.

### Reply handling mode

The first Telegram interaction implementation uses a poll-once command instead of a long-running worker or webhook.

Reason:

- It is simpler to test and reason about.
- It keeps milestone 7 small and usable without requiring deployment infrastructure.
- It can later be wrapped by automation in the next milestone.

### Telegram state source

Telegram interaction stores active menu state and last processed update ID locally in `var/state/telegram_state.json`.

Reason:

- Numeric replies must be mapped back to the exact digest menu that was sent.
- The last processed update ID prevents duplicate reply handling across poll runs.
- Local JSON state is sufficient for the current single-user workflow.
