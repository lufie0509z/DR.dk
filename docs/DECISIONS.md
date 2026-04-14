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
