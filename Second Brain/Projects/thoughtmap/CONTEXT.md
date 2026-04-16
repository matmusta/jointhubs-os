---
type: project
status: active
tags: [type/project, project/thoughtmap, project/jointhubs-os]
created: 2026-04-13
updated: 2026-04-16
---

# ThoughtMap Context

## Past

**Origin**: The idea emerged from the need to explore personal thinking patterns over time. Daily notes in Obsidian and voice dictation via Wispr Flow produce a continuous stream of raw thought — but it's trapped in linear files with no way to see topic density, recurring themes, or connections between days. Graphify showed the value of graph-based knowledge exploration; ThoughtMap applies a similar philosophy to the temporal, personal layer — not entities-and-edges, but vectors-and-proximity.

**Key Decisions**:
- 2026-04-13 — Project initiated after brainstorming session. Core insight: Wispr Flow's SQLite database (`flow.sqlite`) stores every dictation with full metadata (text, timestamp, app context, duration, language). This eliminates the need for any Wispr API integration — we read directly from the local DB.
- 2026-04-13 — Decided on `nomic-embed-text v1.5` via Ollama as the embedding model. Rationale: fully local (no API costs), multilingual (critical for mixed en/pl usage), 768 dimensions with Matryoshka support (truncate to 256 for visualization), 8192 token context window. Alternatives considered: OpenAI text-embedding-3-small (API-dependent), all-MiniLM-L6-v2 (no Polish), mxbai-embed-large (heavier at 1024 dims).
- 2026-04-13 — Chose ChromaDB as vector store. Already used in the office_ai project (Asystent Urzędnika), file-based persistent storage, no server process required in simple mode.
- 2026-04-13 — Wispr Flow transcripts that match text in the Obsidian daily `## Logs` section are tagged as `intent: note` (confirmed intentional notes). Unmatched transcripts are classified by app context into categories (coding, browsing, communication, etc.). This gives two layers: deliberate thought capture vs. operational voice commands.
- 2026-04-13 — Output location: `Second Brain/Operations/thoughtmap-out/` following the graphify-out convention. Runtime data (vector DB, cache) in `thoughtmap-data/` at repo root, gitignored.
- 2026-04-13 — Chunking strategy: ~200 tokens, sentence-boundary-aware, 2-sentence overlap, semantic merge when cosine similarity > 0.85. Text cleanup includes broken word rejoining, sentence boundary extension, and markdown artifact stripping.
- 2026-04-13 — Moved to fully Dockerized architecture. Replaced CLI-only design with an HTTP server (`server.py`) that shows a loading page while the pipeline runs, then auto-redirects to the interactive visualization. Ollama runs as a companion container; model pull is handled automatically by the ThoughtMap app on first start.
- 2026-04-13 — Project code relocated from `thoughtmap/` (repo root) to `Second Brain/Projects/thoughtmap/`. The project is a first-class Second Brain project, not a standalone tool.
- 2026-04-15 — Refactored the codebase into explicit packages: `core/` for ingestion/embedding/clustering, `analysis/` for condensation/indexing/NER/reporting, and `web/` for the server and visualization layer. Rationale: keep the root package small, make the pipeline easier to extend, and create a clean place for new analysis stages.
- 2026-04-15 — Added multilingual named entity extraction and contact discovery. Rationale: clusters show topical structure, but people, organizations, projects, and tools need their own layer for navigation and future agent memory. The implementation combines cache-backed regex matching, spaCy NER, project heuristics, fuzzy deduplication, and Ollama summaries.
- 2026-04-15 — Updated repo-level documentation and agent surfaces to make the privacy model explicit: ThoughtMap runs locally by default, while GitHub Copilot remains a cloud service. Added path-scoped ThoughtMap instructions and a shared `jointhubs-os` deep-work agent.
- 2026-04-16 — Added date-range filtering to the condensed visualization and hardened the runtime around optional local inputs. Rationale: the graph needs temporal slicing to make daily and weekly shifts visible, and transient Wispr/Ollama failures should degrade gracefully instead of aborting the entire pipeline.

**Lessons**:
- The raw input text is in two places that partially overlap: Wispr Flow captures everything spoken (including to VS Code), while Obsidian daily logs capture only what was intentionally dictated into notes. The matching mechanism is essential to distinguish deliberate thought from operational commands.
- Embeddings cannot be "decoded" back to text — the transform is lossy. Cluster labeling uses centroid → nearest chunks → keyword extraction instead.
- The Ollama Docker image does not include `curl` or `wget` — use `ollama list` for healthchecks instead.
- Port 11434 conflicts with locally-installed Ollama — the Docker Compose omits host port mapping for the Ollama container (containers communicate internally via Docker network).
- Optional local sources need defensive handling. The Wispr SQLite can be malformed or mid-write, and Ollama model probes can time out even when the model is usable.

---

## Current

**Status**: Active — refactor, NER, and agent/documentation work implemented; end-to-end runtime validated via Docker Compose

**Current Snapshot**:
- Full pipeline expanded and reorganized: extract → chunk → embed → cluster → condense → NER → report/index → viz
- Docker Compose orchestrates everything: `docker compose up --build` → opens at `http://localhost:8585`
- Code is now organized into `core/`, `analysis/`, and `web/` packages with root-level compatibility exports
- Named entity outputs now target `thoughtmap-out/entities/` plus `entities.json` and `_entity-index.md`
- Root and project READMEs now explain the local-first ThoughtMap runtime separately from Copilot's cloud execution
- Repo automation layer now includes `.github/instructions/thoughtmap.instructions.md` and `.github/agents/jointhubs-os.agent.md`
- Post-refactor import smoke test passed and the Docker stack rebuilt successfully
- The live Docker run now completes extraction, embedding, clustering, entity extraction, and report generation after fixing two `ner.py` syntax regressions discovered only at runtime
- Direct post-cluster validation inside the container now reproduces entity extraction and report generation deterministically from `chunks.json` + `clusters.json`
- NER output is now bounded and operationally safe: total retained entities capped at 250, Ollama summaries capped at 50, remaining entities receive fallback summaries
- Entity/contact-discovery outputs are generated successfully: `entities.json`, per-entity notes, `_entity-index.md`, and entity sections inside `REPORT.md`
- Report quality is materially improved versus the first runs: obvious false positives like task phrases and markdown-link tails were filtered out of the main report tables
- Remaining quality issue is precision in the long tail of entity extraction, especially some organization/location noise and a few residual person false positives in `_entity-index.md`; this is a quality-tuning problem, not a pipeline blocker
- Condensed HTML now exposes time filters for `All Time`, `Today`, `Yesterday`, `This Week`, `This Month`, `This Year`, `Last 2 Years`, plus a custom date range. Cluster and super-cluster metadata now include date ranges so filtering works client-side.
- Runtime hardening is in place for unstable local inputs: Wispr extraction now uses a copied SQLite snapshot and degrades cleanly on DB errors, while Ollama embedding sanitizes inputs, retries transient failures, and steps down to shorter fallbacks instead of failing the whole run on one bad chunk.
- First run processed **340 chunks** from 4 sources:
  - 186 from Obsidian daily notes (Logs, Dziennik, ideation)
  - 77 from Wispr Flow dictation
  - 66 from Obsidian root topic notes
  - 11 from jointhubs-os AI reviews
- 2 topic clusters detected: "Fenix / File / Created" (263 chunks) and "Priority / Google / Obsidian" (77 chunks)
- 16 Wispr entries matched as intentional notes (`intent: note`)
- All code lives in `Second Brain/Projects/thoughtmap/`
- Output lands in `Second Brain/Operations/thoughtmap-out/`

**Files**:

| File | Purpose |
|------|---------|
| `config.py` | Central configuration, env var overrides for Docker |
| `core/extract.py` | Reads all 4 data sources, fuzzy-matches Wispr ↔ Obsidian |
| `core/chunk.py` | Smart chunking with sentence boundaries, overlap, cleanup |
| `core/embed.py` | Ollama API wrapper + ChromaDB storage |
| `core/cluster.py` | UMAP reduction + HDBSCAN clustering + centroid labeling |
| `analysis/condense.py` | Generates condensed cluster narratives |
| `analysis/ner.py` | Extracts people, orgs, projects, tools, and locations |
| `analysis/report.py` | Generates REPORT.md with summaries and entity overview |
| `web/viz.py` | Generates interactive HTML (D3.js scatter plot) |
| `web/server.py` | HTTP server with loading page + pipeline orchestration |
| `run.py` | CLI pipeline runner |
| `Dockerfile` | Python 3.11 image with all dependencies |
| `docker-compose.yml` | Ollama + ThoughtMap containers |
| `.env` / `.env.example` | Local data paths for Docker volume mounts |

**Architecture**:

```
Data Sources                    Pipeline                      Output
─────────────                   ────────                      ──────

Obsidian Daily Notes ─┐
  (## Logs section)   │
                      ├→ extract.py ──→ chunk.py ──→ embed.py ──→ cluster.py ──→ report.py + viz.py
Obsidian Root Notes ──┤     │                                        │
                      │     │ fuzzy match                            │
jointhubs-os Reviews ─┤     ▼                                        ▼
                      │  Wispr entries                          thoughtmap-out/
Wispr Flow SQLite ────┘  matched? ─→ intent: note              ├── REPORT.md
                         not matched? ─→ classify by app       ├── thoughtmap.html
                                         (coding/browsing/     ├── chunks.json
                                          communication/other) └── clusters.json
```

**Wispr Flow Matching & Classification**:

| Match Status | Tag | Description |
|---|---|---|
| Matched in Obsidian `## Logs` | `intent: note` | Confirmed intentional thought capture. User chose to save this in their daily log. |
| Unmatched — app: Code/Terminal | `category: coding` | Commands, instructions, and thoughts spoken while programming. |
| Unmatched — app: Chrome/Edge/Firefox | `category: browsing` | Thoughts during web browsing, research, reading. |
| Unmatched — app: Obsidian (not in Logs) | `category: note-taking` | Dictation in Obsidian that didn't land in the Logs section (maybe in other files). |
| Unmatched — app: Discord/Slack/WhatsApp | `category: communication` | Messages composed via voice. |
| Unmatched — other/unknown app | `category: general` | Everything else. |

**Matching Algorithm**:
1. For each day, extract all text under `## Logs` from the Obsidian daily note
2. For each Wispr `History` entry on the same day where `app = 'Obsidian'`:
   - Compare `formattedText` against Logs content using substring matching (the Wispr text is literally pasted into Obsidian, so it should appear verbatim or near-verbatim)
   - Use normalized Levenshtein distance < 0.15 as the match threshold (accounting for minor formatting differences)
3. Matched entries: `intent: note`, unmatched: classify by `app` field

**Tasks**:

Phase 1 — Core pipeline: ✅
- [x] `extract.py` — read all four data sources, extract text segments with timestamps
- [x] `chunk.py` — smart chunking with sentence boundaries, overlap, semantic merge, cleanup
- [x] `embed.py` — Ollama wrapper for nomic-embed-text, ChromaDB storage
- [x] `cluster.py` — UMAP reduction + HDBSCAN clustering + centroid labeling
- [x] `report.py` — generate REPORT.md with cluster summary, god nodes, density metrics
- [x] `viz.py` — generate interactive HTML with semantic + timeline views
- [x] `config.py` — paths, thresholds, model config (with env var overrides)
- [x] `run.py` + `server.py` — CLI and web server entry points
- [x] `Dockerfile` + `docker-compose.yml` — fully containerized deployment
- [x] `.gitignore` updated for `thoughtmap-data/`

Phase 2 — Wispr integration: ✅
- [x] Wispr Flow SQLite reader in `extract.py`
- [x] Fuzzy matching between Wispr entries and Obsidian Logs
- [x] App-based classification for unmatched entries
- [x] `intent` and `category` metadata in chunk pipeline

Phase 3 — Structure, privacy, and discovery: ✅
- [x] Reorganize code into `core/`, `analysis/`, and `web/`
- [x] Add privacy/local-first documentation to root and project READMEs
- [x] Add multilingual NER with cache-backed discovery and entity note generation
- [x] Add repo-scoped ThoughtMap instructions
- [x] Add shared `jointhubs-os` agent
- [x] Validate Docker runtime end to end, including NER outputs and generated entity reports

Phase 4 — Polish:
- [ ] Incremental processing (file hash cache, skip already-embedded chunks)
- [ ] Windows Task Scheduler / cron for nightly runs
- [ ] Graphify integration (graph of ThoughtMap project itself)
- [ ] Improve cluster labeling (TF-IDF instead of simple frequency)
- [ ] Add search endpoint to web server

**Tech Stack**:
- Python 3.11+
- Ollama + `nomic-embed-text:v1.5`
- ChromaDB (persistent file-based)
- UMAP (`umap-learn`), HDBSCAN (`hdbscan`)
- D3.js (visualization)
- Docker Compose (Ollama provisioning)

---

## Future

**Next Milestone**: Incremental processing — skip already-embedded chunks via hash cache, so nightly runs only process new data.

**End Goal**: A tool that runs nightly, silently processes the day's thoughts, and produces an always-current interactive map of thinking patterns. Over time it becomes a personal cognitive observatory — showing not just what you thought, but how your thinking *moved* across topics, projects, and concerns.

**Open Questions**:
- Should old chunks (pre-2026) ever be backfilled, or is the system strictly forward-looking?
- When clusters change significantly between runs (topic drift), should the report highlight what shifted?
- Should the report be linked from the daily note template (e.g., embed `![[thoughtmap-out/REPORT.md]]`)?
- What minimum chunk count per cluster is meaningful? (2 chunks = noise? 5+ = real topic?)
- Should the vis include a search/query mode (type a question → highlight nearest chunks)?
