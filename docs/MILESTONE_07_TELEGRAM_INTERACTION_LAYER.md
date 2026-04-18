# Milestone 7: Telegram Interaction Layer

## Scope

This milestone adds Telegram Bot API integration for sending the digest and responding to numeric follow-up replies.

Implemented:

- send stored digest batches to Telegram
- persist the active digest menu and chat state locally
- poll Telegram once for updates
- respond to numeric replies with the matching detail artifact

Out of scope:

- webhook deployment
- long-running background worker
- inline button callbacks
- daily scheduling

## Interaction strategy

Telegram interaction is implemented in a minimal, testable form:

1. send the digest batches
2. store the active menu path and chat ID
3. poll updates once
4. if a numeric message like `3` appears, generate and send the corresponding detail response

## What was implemented

### Telegram publish module

- [telegram.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/publish/telegram.py) adds:
  - `sendMessage`
  - `getUpdates`
  - batch sending for digest text files

### Local state storage

- [state.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/storage/state.py) stores:
  - active menu path
  - active chat ID
  - last processed update ID

### CLI support

- [cli.py](/Users/xinyi/Desktop/code/DR.dk/src/dr_digest/cli.py) adds:
  - `telegram-send-digest`
  - `telegram-send-detail`
  - `telegram-poll-once`

## Configuration

- [.env.example](/Users/xinyi/Desktop/code/DR.dk/.env.example) now includes:
  - `STATE_STORAGE_DIR`
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
  - `TELEGRAM_POLL_TIMEOUT`

## Verification

Verified with:

- publish tests for Telegram batch sending
- state storage tests
- CLI tests for digest send, detail send, and poll-once reply handling
- full test suite and bytecode compilation

## Result

Milestone 7 is complete. The project can now send the digest to Telegram and respond to numeric follow-up replies with the corresponding detail content.
