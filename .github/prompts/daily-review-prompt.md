# Daily Review — Cloud Desktop Scheduled Task

You are running the end-of-day review for Stachu (Mateusz Stachowicz). Today's date is {TODAY_DATE}. Run every step carefully and save a complete review note at the end.

**Core rule:** Be efficient with browsing. Do NOT re-read or re-screenshot messages already covered in previous reviews. Always check what the last review already captured before opening any communication channel.

---

## STEP 0 — Load previous reviews + build message watermark

Read the last 3 daily review files from:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Personal\daily\`

Files: `{YESTERDAY_DATE}-review.md`, `{2_DAYS_AGO}-review.md`, `{3_DAYS_AGO}-review.md` (up to 5 days back if gaps exist).

Extract:
- **Message watermark** — note the latest message date/sender already logged per channel (Gmail, Discord, LinkedIn). In subsequent steps, only read messages NEWER than this watermark. This prevents duplicate scanning.
- **Carry-forward items** — unresolved action items, blockers, open questions
- **Recurring themes** — patterns across days (anything appearing 3+ times = trend)
- **People tracker** — which people had pending responses or open threads

Keep a running carry-forward list — you'll merge it at the end.

---

## STEP 1 — Discover and load graphify graphs

Scan for all `graphify-out/GRAPH_REPORT.md` files under:
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\`
- `C:\Users\mateu\Documents\Obsidian Vault\`

**Currently known graphs (list grows over time):**
- `Second Brain/Personal/Profile/graphify-out/` — professional identity
- `Second Brain/Projects/jointhubs/graphify-out-strategic/` — full project graph

For each graph found, read `GRAPH_REPORT.md`. Select 1-2 most relevant to today's context:
- Note active communities, God Nodes, and Surprising Connections
- Check build date — if >2 weeks old and folder changed heavily, flag as stale

**Confidence levels:** `EXTRACTED` = safe to rely on · `INFERRED` = confirm in source · `AMBIGUOUS` = flag as open question only

---

## STEP 2 — Gmail scan (watermark-aware)

Search Gmail for messages received since the message watermark from Step 0 (or last 96h if no watermark exists).

Focus on:
- Direct messages or replies (skip newsletters/automated unless action-required)
- Anything mentioning Fenix, Neurohubs, Asystent Urzędnika, jointhubs
- Urgent or action-required items

Log each message with: `| Sender | Subject | Date | Priority | Response needed? |`

Priority: 🔴 critical · 🟡 important · ℹ️ informational

---

## STEP 3 — Google Calendar + time-block planning

### 3a — Review past & current
Check today's calendar events and tasks and any events and tasks from the past week that may need follow-ups.

### 3b — Week-ahead scan + free time mapping
Check the next 7 days. For each day, map:
- Blocked time (meetings, events)
- **GlobalLogic working hours: 09:00–16:00 Mon–Fri** (treat as soft-block — sometimes available for own work, but don't schedule important own-work there by default)
- Free time blocks available for task scheduling

Output a simple availability grid:
```
| Day        | GL Hours    | Meetings     | Free blocks (own work) |
|------------|-------------|--------------|------------------------|
| Wed 15 Apr | 09:00-16:00 | 14:00 standup| 07:00-09:00, 16:00-19:00 |
```

### 3c — Google Tasks: full sync
Pull all tasks from Google Tasks (all lists). For each task:
- Note: title, due date, status, list name, notes
- Cross-reference with carry-forward items from Step 0 — deduplicate
- Flag overdue tasks (due date < today) as 🔴
- Flag tasks without due dates that have been sitting >7 days

Merge into the master task list used in Step 11.

**Task creation:** When creating new action items in later steps (11, 9d), also create corresponding Google Tasks with due dates so they appear in Calendar.

---

## STEP 4 — Obsidian vault: daily note + modified files + task scan

Read today's daily note if it exists:
`C:\Users\mateu\Documents\Obsidian Vault\10. Operations\Daily\{TODAY_DATE}.md`

Scan for recently modified/created files (last 24h, exclude .git):
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\`
- `C:\Users\mateu\Documents\Obsidian Vault\`

Summarize what changed. Cross-reference with graphify graphs — if a changed file maps to a god node or bridge node, flag as higher signal.

### 4b — Scan for Obsidian Tasks in vault notes

Search all recently modified `.md` files (and today's daily note) for **Obsidian Tasks plugin** tasks. These are NOT regular checkboxes — they are identifiable by emoji markers for dates and priority.

**Regex pattern** (use on each `.md` file content):
```
^- \[.\] .+(📅|🛫|⏳|➕).*(⏫|🔼|🔺|🔽)|^- \[.\] .+(⏫|🔼|🔺|🔽).*(📅|🛫|⏳|➕)
```

This matches lines like:
```
- [ ] jointhubs-os release 📅 2026-04-15 🛫 2026-04-15 🔺 ➕ 2026-04-15
- [x] update CONTEXT.md 📅 2026-04-10 ⏫
- [ ] call Anna Buchwald 🛫 2026-04-16 📅 2026-04-18 🔼 ➕ 2026-04-12
```

**Emoji legend:**
| Emoji | Meaning |
|-------|---------|
| `📅`  | Due date |
| `🛫`  | Start date |
| `⏳`  | Scheduled date |
| `➕`  | Created date |
| `⏫`  | Highest priority |
| `🔼`  | High priority |
| `🔺`  | Medium priority |
| `🔽`  | Low priority |

**Rules:**
- A valid Obsidian Task must have **at least one date emoji** AND **a priority emoji** — ignore plain `- [ ]` checkboxes without these markers
- `- [ ]` = open task, `- [x]` = completed task
- Extract: task name, status (open/done), all dates, priority, source file path
- Note which file each task lives in — this tells you where Stachu defined it

**Where to search:**
1. Obsidian Vault `C:\Users\mateu\Documents\Obsidian Vault\`


**Output as table:**
```
| Task | Priority | 📅 Due | 🛫 Start | Status | Source file |
|------|----------|--------|----------|--------|-------------|
```

These tasks feed into Step 11a — they represent commitments Stachu wrote directly in his notes and must be cross-referenced with Google Tasks to avoid duplication or orphaning.

---

## STEP 5 — Folder health: size & change monitoring

Monitor key directories for growth, unexpected changes, or bloat. Run a quick size scan:

**Directories to monitor:**
- `C:\Users\mateu\Documents\GitHub\` — all repos (list each subfolder with size)
- `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\` — vault inside repo
- `C:\Users\mateu\Documents\Obsidian Vault\` — main Obsidian vault

**For each directory, report:**
```
| Folder                          | Size    | Files | Change vs last review |
|---------------------------------|---------|-------|-----------------------|
| GitHub\jointhubs-os             | 245 MB  | 1,203 | +12 MB (+8 files)     |
| GitHub\jointhubs-fenix\office   | 89 MB   | 412   | no change             |
| Obsidian Vault                  | 310 MB  | 2,100 | +3 MB (+5 files)      |
```

**Flag if:**
- Any folder grew >50 MB since last review (possible large file committed or generated output left behind)
- A repo folder has uncommitted changes (dirty working tree)
- `node_modules`, `__pycache__`, `.venv`, or `data/` folders are unusually large

Use PowerShell: `Get-ChildItem -Directory | ForEach-Object { $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; [PSCustomObject]@{Name=$_.Name; SizeMB=[math]::Round($size/1MB,1)} }`

Compare with the previous review's folder sizes (from Step 0 carry-forward). If no previous data exists, establish baseline.

---

## STEP 6 — Discord (watermark-aware, selective)

**Before opening Discord**, check the message watermark from Step 0. Only read messages NEWER than the last logged date per contact.

Check:
- Direct Messages — unread only
- Jointhubs server — relevant channels only, last 96h

**Do NOT** read or summarize messages from any other server.

Log new messages with: `| Contact | Last message | Date | Status | Channel |`

Status: ✅ answered · ⌛ pending reply · 🔴 overdue (>3 days)

If Chrome unavailable, skip.

---

## STEP 7 — LinkedIn (file-based tracking only)

**Do NOT open LinkedIn in browser.** Instead, maintain a communication log file:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Personal\peers\linkedin-tracker.md`

If the file exists, read it. If not, create it with this structure:

```markdown
---
type: communication-tracker
platform: linkedin
updated: {TODAY_DATE}
---

# LinkedIn Communication Tracker

## Active Threads
| Contact | Last message from them | Last message from me | Status | Topic |
|---------|----------------------|---------------------|--------|-------|

## Pending Outreach
| Contact | Purpose | Priority | Added |
|---------|---------|----------|-------|
```

Cross-reference with peer notes in `Second Brain/Personal/peers/` and any LinkedIn mentions from Gmail notifications or previous reviews. Update the tracker with any new information found indirectly.

---

## STEP 8 — Communication map (per-person, cross-channel)

Build or update a communication overview file:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Personal\peers\communication-map.md`

Structure:

```markdown
---
type: communication-map
updated: {TODAY_DATE}
---

# Communication Map

## Active contacts (last 2 weeks)
| Person | Channels | Last contact | Open thread? | Peer note exists? |
|--------|----------|-------------|-------------|-------------------|
| Anna Buchwald | Discord, Email | 2026-04-08 | ⌛ waiting | ❌ create |
```

For each person appearing in today's scan:
- Note which channel(s) the conversation is on
- Flag if peer note (`Second Brain/Personal/peers/`) is missing → suggest creating it
- Track response age — if >5 days without response, flag 🔴

---

## STEP 9 — ThoughtMap ChromaDB: semantic memory recall

Query the ThoughtMap ChromaDB vector database to enrich today's review with historical context. This is your long-term memory — use it to connect today's topics with past thinking, decisions, and patterns.

### 9a — Extract today's key topics

From Steps 0-8, identify the **5-8 most significant topics, names, or concepts** discussed today. Examples:
- Project names: "Fenix demo", "Asystent Urzędnika deployment"
- People: "Anna Buchwald", "Artur Povodor"
- Technical topics: "RAG pipeline", "Docker security"
- Decisions or blockers: "pricing strategy", "AWS billing"

### 9b — Query ChromaDB

For each key topic, run a semantic similarity search against the ThoughtMap collection.

**Database location:** `C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\thoughtmap\data\chroma\`
**Collection name:** `thoughtmap`

**Query method — run this Python script** (requires the thoughtmap venv):

```python
import chromadb

client = chromadb.PersistentClient(
    path=r"C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Projects\thoughtmap\data\chroma"
)
collection = client.get_collection("thoughtmap")

queries = [
    "Fenix demo preparation",
    "Anna Buchwald collaboration",
    # ... add today's key topics here
]

for q in queries:
    results = collection.query(
        query_texts=[q],
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    print(f"\n--- {q} ---")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist < 0.65:  # cosine distance threshold — only relevant results
            print(f"  [{meta.get('timestamp','?')[:10]}] (dist={dist:.3f}) {doc[:200]}")
```

**If Ollama is not running** (embedding model needed for query), fall back to reading the pre-built cluster files:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Operations\thoughtmap-out\clusters\*.md`

Scan cluster titles for topic matches and read the relevant cluster files for context.

### 9c — Analyze historical context

For each topic with ChromaDB results:
1. **History exists** — What was said before about this topic? When? What was decided?
2. **Pattern detection** — Does this topic keep recurring without resolution? Flag it.
3. **Connections** — Do results from different queries overlap? That's a cross-domain signal.
4. **Staleness** — If the most recent chunk is >30 days old, the topic may have drifted.

### 9d — Generate context-aware suggestions

Based on historical context, produce for each active topic:
- **Previously explored** — "This was discussed on [date], decision was [X]" or "You considered [Y] but didn't pursue it"
- **Recurring without closure** — "This topic appeared [N] times in the last month without being resolved"
- **New direction proposals** — Based on what's in the history + what happened today, suggest 1-2 concrete next steps or angles not yet explored

Output this as a dedicated section in the review (see Step 14 template).

---

## STEP 10 — Day reflection + analysis

Based on everything gathered, write an honest end-of-day reflection:

### 🏆 Co poszło dobrze (What went well)
- 3-5 concrete wins, achievements, or positive signals from today
- Include small wins (answered a long-pending email, shipped a commit, had a good call)

### ⚡ Winy dnia (Today's shortcomings)
- What didn't get done that should have?
- Where was time wasted or focus lost?
- Any dropped balls or missed commitments?
- Be specific and honest, not vague

### 🔭 Na co zwrócić uwagę (Watch-outs for the future)
- Patterns that could become problems if ignored
- Deadlines approaching
- Relationships that need attention
- Technical debt or process gaps spotted

### 💡 Co mogłem zrobić lepiej (What could I have done better)
- Specific, actionable improvements — not generic advice
- Reference today's actual events
- 1-3 items max

---

## STEP 11 — Task migration + scheduling

### 11a — Collect all open tasks
Gather tasks from:
- Today's carry-forward list
- New action items from Steps 2-8
- Incomplete tasks from today's daily note
- **Obsidian Tasks found in Step 4b** (vault notes with 📅/🛫/⏳ + priority emoji)
- Google Tasks

Cross-reference Obsidian Tasks (Step 4b) with Google Tasks (Step 3c) — deduplicate by matching task names. If an Obsidian Task has no matching Google Task and is still open, flag it for Google Tasks creation in Step 11e so it appears in Calendar.

### 11b — Triage and prioritize
For each task, assign:
- Priority: 🔴 critical · 🟡 important · ⚪ low
- Estimated time: (15m / 30m / 1h / 2h / half-day)
- Deadline if known

### 11c — Schedule into calendar free blocks
Using the availability grid from Step 3b, suggest concrete time blocks for top-priority tasks:

```
📅 Suggested schedule:
- Wed 15 Apr, 16:30-17:30 → 🔴 Prepare Fenix demo (1h)
- Wed 15 Apr, 17:30-18:00 → 🟡 Reply to Anna Buchwald (30m)
- Thu 16 Apr, 07:00-08:00 → 🟡 Review SCE paper (1h)
```

Rules:
- **09:00-16:00 Mon-Fri = GlobalLogic** — only schedule own-work there if explicitly low-load day
- Prefer morning blocks (before 09:00) for deep work
- Prefer evening blocks (16:00-19:00) for calls and communication
- Don't overload any single day — max 3h of scheduled own-work outside GL hours
- Weekend blocks only for 🔴 critical items

### 11d — Tasks that need calendar events
If a task requires a specific time (call, meeting, deadline), suggest creating a Google Calendar event with exact details.

### 11e — Plan Google Tasks for the future
For tasks that don't fit in the next 3 days, create Google Tasks with appropriate due dates. Group by project/context. Ensure every action item from the review has either:
- A time block in the suggested schedule (next 3 days), OR
- A Google Task with a due date (further out)

No task should be orphaned — everything gets tracked somewhere.

### 11f — Schedule Wispr Flow recording sessions
Based on the ThoughtMap analysis (Step 9) and today's open questions, identify **1-2 topics** that would benefit from a 15-30 minute voice deep-dive. These are topics where:
- There's a gap in documented thinking (ChromaDB has surface-level chunks but no depth)
- A decision is stalled because the reasoning hasn't been articulated
- Multiple threads converge and need synthesis
- A recurring carry-forward item needs unblocking through reflection

For each proposed session, create:
```
🎙️ Wispr Recording Session
- Topic: [specific question or theme]
- Guiding questions: [2-3 questions to answer during recording]
- Context to review first: [links to relevant notes/files]
- Suggested slot: [date, time block from availability grid]
- Expected output: [what note should be created/updated in Second Brain]
```

Schedule these in free blocks — preferably morning (07:00-09:00) when thinking is freshest. Max 1 session per day.

---

## STEP 12 — Process Wispr Flow transcripts

Check for new Wispr Flow transcriptions that haven't been processed yet.

**How to detect new transcripts:**
Wispr Flow saves transcriptions to the SQLite database at:
`C:\Users\mateu\AppData\Roaming\Wispr Flow\flow.sqlite`

ThoughtMap already extracts these during its pipeline. Check for recent chunks in ChromaDB with `source: wispr-flow` and `timestamp > {YESTERDAY_DATE}`.

Alternatively, check today's daily note in Obsidian — Wispr transcriptions often appear there as raw text blocks.

**Processing rules:**
1. **Identify the topic** — What was the recording about? Match against existing Second Brain notes.
2. **Route the content:**
   - If the transcript answers a previously scheduled recording session (from a prior review's `🎙️ Wispr Recording Session`) → create or update the designated Second Brain note
   - If it's a standalone reflection → extract key points into today's daily review under a `## Wispr Insights` section
   - If it covers a specific project → update or create a note in the relevant `Second Brain/Projects/{project}/` folder
   - If it's about a person → update their peer note in `Second Brain/Personal/peers/`
3. **Extract structured data:**
   - Decisions made → log with date
   - Action items mentioned → add to task list (Step 11)
   - Questions raised → add to Follow-Up Questions
   - New ideas → note under the relevant project or create a new note
4. **Link back** — Add `[[{note_name}]]` wikilinks in the daily review pointing to any notes created/updated from transcripts

**Note creation format** (when creating new Second Brain notes from transcripts):
```markdown
---
type: insight
source: wispr-flow
date: {TODAY_DATE}
project: [project-tag]
status: active
---

# [Topic Title]

## Context
[Why this recording was made — link to the review that scheduled it]

## Key Points
[Extracted from transcript]

## Decisions
[Any decisions articulated]

## Open Questions
[Remaining unknowns]

## Next Steps
[Action items]
```

---

## STEP 13 — Peer network check

Cross-reference all people mentioned today with `Second Brain/Personal/peers/`:
- If a significant person has no peer note → flag: "Create peer note for [name]"
- If a peer note exists but is outdated (last updated >30 days ago) → flag for update
- Read relevant peer notes for context on active relationships

---

## STEP 14 — Graph insights

Based on graphify graphs loaded in Step 1:
1. **Graph-signal connections** — map today's events to specific communities or god nodes
2. **Silent communities** — any community that should be active but has no signals today
3. **Cross-domain bridges** — surprising connections between today's inputs
4. **Staleness check** — flag any graph that needs rebuild

---

## STEP 15 — Save output

Save the review to:
`C:\Users\mateu\Documents\GitHub\jointhubs-os\Second Brain\Personal\daily\{TODAY_DATE}-review.md`

```markdown
---
date: {TODAY_DATE}
type: daily-review
---

# Daily Review — {TODAY_DATE}

## Summary
[3-5 bullet points of the most important things today]

## Graphs Loaded (graphify)
[Table: graph path, nodes, edges, communities, build date, relevance]

## Gmail
[New messages since watermark, formatted as table]

## Calendar
[Today's events + week-ahead availability grid]

## Modified Files (last 24h)
[Changed files with graph cross-reference flags]

## Folder Health
[Size table for monitored directories with change vs last review]

## Discord
[New messages since watermark, by contact]

## LinkedIn (tracked)
[Updates from linkedin-tracker.md, no direct browsing]

## Communication Map Updates
[Per-person cross-channel summary, new contacts flagged]

## Carry-Forward
| Sprawa | Od kiedy | Dni | Status |
|--------|----------|-----|--------|
[Tracked items with age in days and emoji priority]

## 🏆 Co poszło dobrze
[3-5 wins]

## ⚡ Winy dnia
[Honest shortcomings]

## 🔭 Na co zwrócić uwagę
[Watch-outs and patterns]

## 💡 Co mogłem zrobić lepiej
[Specific improvements]

## Action Items
[Prioritized, numbered list with 🔴/🟡/⚪]

## Google Tasks
[Full task list synced from Google Tasks — overdue flagged, new tasks created]

## 📅 Suggested Schedule (next 3 days)
[Time-blocked task suggestions mapped to free calendar slots]

## 🎙️ Wispr Recording Sessions (planned)
[1-2 proposed voice deep-dive sessions with topic, guiding questions, and suggested time slot]

## Wispr Insights (processed)
[Key points extracted from today's Wispr transcripts, with links to created/updated notes]

## 🧠 ThoughtMap Memory
[Per-topic historical context from ChromaDB]

### Previously explored
[Topics that were already discussed, with dates and decisions]

### Recurring without closure
[Topics appearing repeatedly without resolution — with count and first mention date]

### New directions
[1-3 concrete suggestions based on history + today's context]

## Graph Insights
[1-2 observations anchored in graph data]

## Follow-Up Questions
[2-4 questions for Stachu to think about or act on]

## Tips & Observations
[1-2 proactive suggestions based on weekly patterns]
```

If any section was unavailable (Chrome offline, API blocked), note it clearly rather than leaving blank.

---

## Operational rules

1. **Screenshot discipline** — Only take screenshots when text extraction fails. Prefer reading page content directly. Never screenshot full feeds or timelines.
2. **Message deduplication** — The watermark from Step 0 is law. Never re-summarize a message already in a previous review unless its status changed.
3. **Time awareness** — All scheduling respects GlobalLogic 09:00-16:00 constraint. Stachu's productive own-work hours are typically 07:00-09:00 and 16:00-20:00.
4. **Polish/English** — Section headers in English, content can mix Polish and English naturally as Stachu does.
5. **Peer tracking** — Every person mentioned in any channel gets checked against `peers/`. Missing = flag for creation.
6. **File creation** — Create `linkedin-tracker.md` and `communication-map.md` only if they don't exist yet. Update in-place on subsequent runs.
7. **Google Tasks sync** — Every action item must be tracked: either as a time block in the schedule or as a Google Task with a due date. No orphaned tasks.
8. **Wispr Flow sessions** — Propose max 1 recording session per day. Pick topics where voice articulation will unlock progress faster than writing. Always provide guiding questions so the recording is focused.
9. **Wispr transcript processing** — When processing transcripts, prefer updating existing notes over creating new ones. Only create a new note when the topic doesn't have a home yet in Second Brain. Always link back from the daily review.
10. **Second Brain note creation** — When creating notes from any source (Wispr, analysis, synthesis), follow the vault conventions: frontmatter with type/status/date, proper folder placement, wikilinks to related notes.
