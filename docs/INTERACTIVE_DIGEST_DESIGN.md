# Interactive Digest Design

## Product direction

The product should not depend on strict top-N selection as its primary user experience.

Instead, it should send a compact daily digest of all DR stories and let the user ask for more detail on demand.

## User experience

### Step 1: Daily digest

Send one or more Telegram messages containing a numbered list of the day's stories.

Each item should include:

- item number
- title
- one-sentence summary
- optional English and Chinese translation when available

Example:

```text
1. Temporary border controls against Germany extended again
2. Copenhagen Municipality wins housing case
3. Warning about fake SMS messages
```

### Step 2: Follow-up detail

If the user replies with a number such as `3`, the bot should send a longer summary for story 3.

Possible later extensions:

- `3 en`
- `3 zh`
- `more 3`
- inline Telegram buttons instead of text replies

## Why this direction is better

- It avoids missing stories the user personally cares about.
- It keeps the first message compact and scannable.
- It fits Telegram's interactive chat model.
- It reduces the pressure to perfect selection before the product is useful.

## Required content layers

### Short layer

Used in the daily digest:

- title
- one-sentence summary
- item number

### Long layer

Used only on request:

- longer summary
- optional key points
- source link
- optional bilingual output

## Architectural implications

The product now needs:

- short-summary generation for every story
- stable numbering or IDs for stories within each digest
- persisted digest state so a user reply can be mapped back to the correct story
- Telegram interaction handling for follow-up replies

The product no longer depends on strict top-N preselection as its primary interaction model.

## Recommended message strategy

Sending 50 stories in a single long message is not ideal.

Recommended formats:

- send the list in batches
- or send a main digest plus a `more` flow
- or send all items, but grouped and compactly formatted

Practical first version:

- send items in numbered batches of 10
- store the batch and item mapping locally
- accept reply numbers for long summaries

## Next implementation milestones

### Milestone 4: Short summaries for all stories

- generate one-sentence summaries for every ingested story
- save them in a digest-oriented artifact

### Milestone 5: Daily digest assembly

- build the numbered digest message
- preserve stable item ordering
- store digest metadata for later lookup

### Milestone 6: Interactive detail lookup

- map user reply numbers back to stored items
- generate and send long summaries on demand

### Milestone 7: Telegram interaction layer

- send the digest to Telegram
- receive reply commands or button actions
- return the detailed summary for the chosen story

### Milestone 8: Automation

- run the daily digest automatically
- keep digest state for the active day
- avoid duplicate sends unless explicitly forced
