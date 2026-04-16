---
type: prd
project: thoughtmap
status: active
created: 2026-04-15
updated: 2026-04-15
---

# ThoughtMap — Product Requirements Document

## Overview

ThoughtMap is a local-first personal knowledge pipeline that extracts text from multiple sources (Obsidian vault, Wispr Flow dictations, Second Brain markdown), embeds it via Ollama, clusters it into topic groups, and visualizes connections in an interactive graph.

This PRD covers **five features** to be implemented sequentially:

1. **Folder Reorganization** — restructure flat Python modules into logical packages
2. **README & Privacy** — user-facing documentation and data privacy statement
3. **Named Entity Recognition** — auto-extract people, orgs, projects from clusters
4. **jointhubs-os Agent** — VS Code Copilot agent for deep work sessions
5. **Contact Discovery** — NER-driven contact directory (peers/ stays as-is)

## Implementation Status — 2026-04-15

This PRD is now best treated as an implementation record rather than a forward plan.

- Core scope is implemented: Features 1-5 exist in the codebase and have been exercised end to end through the Dockerized runtime.
- The main remaining issue is **quality**, not missing functionality: NER still produces long-tail false positives in generated entity outputs, especially some organization/location entries and a few residual person mistakes.
- One verification step remains inherently manual: confirming the `jointhubs-os` agent appears in the Copilot UI picker on the current machine.
- A follow-up precision pass on 2026-04-15 tightened validator rules and fixed stale entity-note regeneration, but the generated `_entity-index.md` still shows substantial organization/location noise, so this backlog item remains open.

### Acceptance Snapshot

| Feature | Status | Evidence | Remaining Gap |
|---|---|---|---|
| 1. Folder Reorganization | Implemented | `core/`, `analysis/`, and `web/` packages exist; `run.py`, `__main__.py`, and `__init__.py` use `thoughtmap.*` imports and compatibility exports | None functionally |
| 2. README & Privacy | Implemented | Root README and ThoughtMap README now describe the local-first ThoughtMap runtime separately from Copilot's cloud execution | None |
| 3. Named Entity Recognition | Implemented with quality debt | `analysis/ner.py`, NER config, Docker spaCy install, entity report section, `entities/`, `_entity-index.md`, `entities.json`, and `data/entities_cache.json` are present | Precision cleanup in generated entity outputs |
| 4. jointhubs-os Agent | Implemented | `.github/agents/jointhubs-os.agent.md`, `.github/instructions/thoughtmap.instructions.md`, and global assistant instructions were added/updated | Manual Copilot UI verification not re-run in this session |
| 5. Contact Discovery | Implemented | Person entity notes are generated and include peer-note source paths; agent instructions explicitly cross-reference `peers/` and ThoughtMap entity notes | None functionally |

### What Still Needs To Be Done

1. Continue precision-only NER cleanup until the generated entity index is materially cleaner for daily use, especially for organization/location outputs.
2. Manually confirm the `jointhubs-os` agent in the VS Code Copilot picker on this machine.
3. Optionally convert the checklist below from design-time acceptance criteria into a fully checked historical record after the two items above are closed.

---

## Architecture Context

### Current Pipeline

```
extract → chunk → embed → cluster → condense → report → viz
```

### Target Pipeline (after NER)

```
extract → chunk → embed → cluster → condense → NER → report → viz
```

### Current File Structure

```
thoughtmap/
├── config.py        (305 lines)   Global configuration
├── run.py           (165 lines)   Pipeline orchestrator
├── __main__.py      (40 lines)    CLI entry point
├── __init__.py      (1 line)      Package init
├── extract.py       (542 lines)   5 data source extractors
├── chunk.py         (318 lines)   Smart chunking
├── embed.py         (280 lines)   Ollama/OpenAI/Google embeddings + ChromaDB
├── cluster.py       (525 lines)   UMAP + HDBSCAN clustering
├── condense.py      (~1000 lines) LLM summaries + super-clusters + HTML viz
├── recluster.py     (72 lines)    Standalone re-cluster script
├── report.py        (118 lines)   REPORT.md generation
├── index.py         (231 lines)   Domain-grouped index notes
├── viz.py           (450 lines)   Interactive HTML visualization
├── server.py        (525 lines)   HTTP server + API endpoints
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Key Technical Details

- **Python 3.11** in Docker container (`python:3.11-slim`)
- **Ollama** for embeddings (`qwen3-embedding:8b`) and summaries (`gemma4:e2b`)
- **ChromaDB** for vector storage (local, persistent at `data/chroma/`)
- **PYTHONPATH=/app** in Docker — package importable as `thoughtmap.*`
- **All imports are relative**: `from . import config`, `from .cluster import ClusterInfo`
- **Output directory**: `Second Brain/Operations/thoughtmap-out/`
- **Server port**: 8585

---

## Feature 1: Folder Reorganization

### Goal

Split 12 flat Python files into 3 logical sub-packages with clear import conventions.

### Target Structure

```
thoughtmap/
├── config.py          # stays — root config, all other modules import from here
├── run.py             # stays — pipeline orchestrator, imports from all sub-packages
├── __main__.py        # stays — CLI entry point
├── __init__.py        # stays — update with re-exports
│
├── core/              # Data pipeline stages 1-6
│   ├── __init__.py    # re-exports: TextSegment, Chunk, ClusterInfo, ThoughtMapResult
│   ├── extract.py     # ← from ./extract.py
│   ├── chunk.py       # ← from ./chunk.py
│   ├── embed.py       # ← from ./embed.py
│   └── cluster.py     # ← from ./cluster.py
│
├── analysis/          # Post-clustering analysis
│   ├── __init__.py    # re-exports: condense, save_report
│   ├── condense.py    # ← from ./condense.py
│   ├── recluster.py   # ← from ./recluster.py
│   ├── report.py      # ← from ./report.py
│   ├── index.py       # ← from ./index.py
│   └── ner.py         # NEW (Feature 3)
│
├── web/               # HTTP server & visualization
│   ├── __init__.py    # re-exports: serve, serve_static
│   ├── server.py      # ← from ./server.py
│   └── viz.py         # ← from ./viz.py
│
├── Dockerfile         # no changes needed (copies whole dir)
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Import Convention (MUST follow everywhere)

```python
# Always use full package paths — never relative shortcuts
from thoughtmap.config import OUTPUT_DIR, OLLAMA_BASE_URL
from thoughtmap.core.extract import extract_all, TextSegment
from thoughtmap.core.chunk import chunk_all, merge_similar_chunks, Chunk
from thoughtmap.core.embed import embed_batch, store_chunks, load_all_embeddings
from thoughtmap.core.cluster import cluster_all, ClusterInfo, ThoughtMapResult
from thoughtmap.analysis.condense import condense
from thoughtmap.analysis.report import save_report, generate_report
from thoughtmap.analysis.index import generate_cluster_indices
from thoughtmap.analysis.ner import extract_entities  # Feature 3
from thoughtmap.web.server import serve, serve_static
from thoughtmap.web.viz import generate_viz
```

### Tasks

| # | Task | File(s) | Acceptance Criteria |
|---|------|---------|-------------------|
| 1.1 | Create sub-package directories | `core/`, `analysis/`, `web/` | Each has `__init__.py` with re-exports |
| 1.2 | Move files with `git mv` | All 12 `.py` files | `git status` shows renames, not delete+create |
| 1.3 | Update imports in `run.py` | [run.py](run.py) | All `from .extract import ...` → `from thoughtmap.core.extract import ...` |
| 1.4 | Update imports in `__main__.py` | [\_\_main\_\_.py](__main__.py) | `from .server import serve` → `from thoughtmap.web.server import serve` |
| 1.5 | Update imports in `condense.py` | [condense.py](condense.py) | `from .cluster import ...` → `from thoughtmap.core.cluster import ...` |
| 1.6 | Update imports in `server.py` | [server.py](server.py) | `from .embed import ...` → `from thoughtmap.core.embed import ...` |
| 1.7 | Update imports in `recluster.py` | [recluster.py](recluster.py) | All imports updated to new paths |
| 1.8 | Update imports in `embed.py` | [embed.py](embed.py) | `from .chunk import Chunk` → `from thoughtmap.core.chunk import Chunk` |
| 1.9 | Update `__init__.py` | [\_\_init\_\_.py](__init__.py) | Add top-level re-exports for backwards compat |
| 1.10 | Verify Docker build | Terminal | `docker compose up -d --build` succeeds |
| 1.11 | Verify pipeline | Terminal | Pipeline completes all 7 steps, `localhost:8585` renders graph |
| 1.12 | Verify imports | Terminal | `python -c "from thoughtmap.core.extract import extract_all; from thoughtmap.analysis.condense import condense; from thoughtmap.web.server import serve; print('OK')"` prints `OK` |

### Gotchas

- **Relative imports in moved files**: Files that import siblings (e.g., `embed.py` imports `from .chunk import Chunk`) need updating to `from thoughtmap.core.chunk import Chunk`
- **Lazy imports in `server.py`**: Server has runtime imports inside handler functions — search for ALL `from .` patterns, not just top-level
- **`condense.py` imports `cluster.py`**: Cross-package reference: `from thoughtmap.core.cluster import ClusterInfo, ThoughtMapResult`
- **Dockerfile doesn't change**: `COPY . /app/thoughtmap/` already copies the whole directory tree
- **PYTHONPATH=/app**: Package path `thoughtmap.core.extract` resolves to `/app/thoughtmap/core/extract.py` — correct

---

## Feature 2: README & Privacy Documentation

### Goal

Clear 2-3 sentence product description + data privacy statement for the root README and ThoughtMap README.

### Tasks

| # | Task | File(s) | Acceptance Criteria |
|---|------|---------|-------------------|
| 2.1 | Update root README intro | [../../README.md](../../../README.md) | Contains 2-3 sentence description (see copy below) |
| 2.2 | Add Privacy & Data section to root README | [../../README.md](../../../README.md) | Section exists with bullet points on local processing |
| 2.3 | Update ThoughtMap README | [README.md](README.md) | Privacy statement about Ollama-only default |

### Copy: Root README Intro

> **Jointhubs OS** is an open-source AI-powered Second Brain — a system of specialized agents, reusable skills, and structured notes that help you plan, build, and reflect across projects. It runs inside VS Code with GitHub Copilot, using your local Obsidian vault as the knowledge layer. The ThoughtMap pipeline (embeddings, clustering, summaries) runs 100% locally through Ollama — nothing leaves your machine. GitHub Copilot agents use cloud-hosted LLMs (e.g. Claude, GPT) and send context to those providers. You choose which parts of your workflow stay local and which leverage cloud AI.

### Copy: Privacy & Data Section

```markdown
## Privacy & Data

- **ThoughtMap pipeline is 100% local** — All embeddings, clustering, and LLM summaries run through Ollama on your machine
- **No telemetry, no cloud sync** — ThoughtMap never sends your notes, thoughts, or dictations off your disk
- **GitHub Copilot agents use cloud LLMs** — When you interact with agents in VS Code, context is sent to the model provider (e.g. Anthropic, OpenAI) per GitHub Copilot's privacy policy
- **Optional cloud embedding providers** — OpenAI and Google embedding APIs available for ThoughtMap if you explicitly set API keys
- **Data sources** — Local Obsidian vault, Wispr Flow SQLite database, repository markdown files
- **Browser dependency** — The visualization page loads vis-network.js from a CDN (the only external network request)
```

---

## Feature 3: Named Entity Recognition (NER)

### Goal

After condensation, automatically extract named entities (people, organizations, projects, tools, locations) from cluster content. Generate per-entity notes with cross-references and Ollama summaries.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NER Pipeline                           │
│                                                             │
│  1. Load cache (entities_cache.json)                        │
│  2. Regex scan: find known entities in all chunks           │
│  3. spaCy scan: extract NEW entities from unmatched chunks  │
│  4. Deduplicate: merge aliases (case, whitespace, fuzzy)    │
│  5. Cross-reference: map entities → clusters → source files │
│  6. Ollama summarize: 2-3 sentence summary per entity       │
│  7. Generate output: markdown notes + entities.json         │
│  8. Update cache                                            │
└─────────────────────────────────────────────────────────────┘
```

### Data Model

```python
@dataclass
class Entity:
    name: str              # Canonical name: "Anna Buchwald"
    type: str              # "person" | "organization" | "project" | "tool" | "location"
    aliases: list[str]     # ["Anna", "Buchwald", "anna buchwald"]
    normalized: str        # Lowercase, no diacritics, no extra spaces: "anna buchwald"
    cluster_ids: list[int] # Clusters where this entity appears
    source_files: list[str] # Source file paths
    mention_count: int     # Total mentions across all chunks
    summary: str           # Ollama-generated 2-3 sentence summary
    first_seen: str        # ISO date of first appearance
```

### Cache Mechanism

**File**: `data/entities_cache.json`

```json
{
  "jan kowalski": {
    "name": "Jan Kowalski",
    "type": "person",
    "aliases": ["Jan", "Kowalski"],
    "normalized": "jan kowalski",
    "first_seen": "2026-03-15"
  },
  "fenix": {
    "name": "Fenix",
    "type": "project",
    "aliases": ["fenix", "Fenix platform"],
    "normalized": "fenix",
    "first_seen": "2026-01-20"
  }
}
```

**Cache logic**:
1. On startup: load `entities_cache.json` (create empty if missing)
2. Build regex patterns from cached entities: case-insensitive, whitespace-flexible
   ```python
   # For "Jan Kowalski" → r'jan\s+kowalski' (case-insensitive)
   # For "Fenix" → r'\bfenix\b' (word boundary)
   ```
3. Scan ALL chunks with regex → mark matched entities + chunk IDs
4. For chunks with NO regex matches → run spaCy NER
5. Merge spaCy-discovered entities with cache (deduplicate)
6. Update cache with new entities
7. Save updated `entities_cache.json`

**Cache invalidation**: 
- Manual: delete `data/entities_cache.json` → full spaCy re-scan
- Automatic: never expires (entities are additive)

### Normalization Rules

```python
def normalize_entity(name: str) -> str:
    """Normalize entity name for dedup and matching."""
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)         # collapse whitespace
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode()  # strip diacritics
    return name
```

**Dedup matching**: Two entities are the same if:
- `normalize_entity(a) == normalize_entity(b)`, OR
- One is a substring of the other AND same type, OR
- Levenshtein distance < 0.15 (reuse existing `python-Levenshtein` dep)

### Ollama Summary Prompt

```
You are analyzing a named entity found across a personal knowledge base.
Below are text fragments where this entity appears.

Entity: {name} (type: {type})
Found in {mention_count} text fragments across {len(cluster_ids)} topic clusters.

Representative mentions:
{fragments}

Write a concise 2-3 sentence summary of this entity's role and context
in the knowledge base. Include relationships to projects, people, or topics
if apparent. Write in the same language as the fragments.
```

### Output Structure

```
thoughtmap-out/
├── entities/
│   ├── _entity-index.md         # Master index table
│   ├── person/
│   │   ├── jan-kowalski.md
│   │   └── konrad-bujak.md
│   ├── organization/
│   │   ├── brainlab.md
│   │   └── jointhubs.md
│   ├── project/
│   │   ├── fenix.md
│   │   └── neurohubs.md
│   ├── tool/
│   │   ├── obsidian.md
│   │   └── ollama.md
│   └── location/
│       └── madrid.md
├── entities.json                # Machine-readable (all entities + metadata)
```

### Entity Note Format

```markdown
---
type: entity
entity_type: person
name: Jan Kowalski
aliases: [Jan, Kowalski]
clusters: [12, 45, 67]
mentions: 15
first_seen: 2026-03-15
generated: 2026-04-15
---

# Jan Kowalski

## Summary

[Ollama-generated 2-3 sentence summary]

## Appearances by Cluster

| Cluster | Label | Mentions |
|---------|-------|----------|
| 12 | BrainLab Research | 5 |
| 45 | Neurohubs Distribution | 8 |
| 67 | EEG Analysis | 2 |

## Source Files

- Second Brain/Projects/neurohubs/CONTEXT.md
- Second Brain/Personal/daily/2026-04-13-review.md
```

### Entity Index Format (`_entity-index.md`)

```markdown
# ThoughtMap Entity Index — 2026-04-15

## Summary
- **{N}** entities discovered across **{M}** clusters
- People: {n} | Organizations: {n} | Projects: {n} | Tools: {n} | Locations: {n}

## People
| Entity | Mentions | Clusters | Summary |
|--------|----------|----------|---------|
| [[person/jan-kowalski\|Jan Kowalski]] | 15 | 3 | EEG research partner... |

## Organizations
...

## Projects
...
```

### Configuration

Add to `config.py`:

```python
# ─── Named Entity Recognition ───
NER_ENABLED = os.environ.get("THOUGHTMAP_NER_ENABLED", "true").lower() == "true"
NER_SPACY_MODEL = os.environ.get("THOUGHTMAP_NER_SPACY_MODEL", "xx_ent_wiki_sm")
NER_MIN_MENTIONS = int(os.environ.get("THOUGHTMAP_NER_MIN_MENTIONS", "2"))
NER_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "PRODUCT", "WORK_OF_ART", "LOC"}
NER_CACHE_FILE = DATA_DIR / "entities_cache.json"
ENTITIES_DIR = OUTPUT_DIR / "entities"
```

Add to `.env.example`:

```env
# Named Entity Recognition
# THOUGHTMAP_NER_ENABLED=true
# THOUGHTMAP_NER_SPACY_MODEL=xx_ent_wiki_sm
# THOUGHTMAP_NER_MIN_MENTIONS=2
```

### Dependencies

Add to `requirements.txt`:
```
spacy>=3.7.0
```

Add to `Dockerfile` (after `pip install`):
```dockerfile
RUN python -m spacy download xx_ent_wiki_sm
```

### Tasks

| # | Task | File(s) | Acceptance Criteria |
|---|------|---------|-------------------|
| 3.1 | Add NER config vars | `config.py` | `NER_ENABLED`, `NER_SPACY_MODEL`, `NER_MIN_MENTIONS`, `NER_ENTITY_TYPES`, `NER_CACHE_FILE`, `ENTITIES_DIR` exist |
| 3.2 | Add `.env.example` entries | `.env.example` | NER env vars documented |
| 3.3 | Add `spacy` to requirements | `requirements.txt` | `spacy>=3.7.0` present |
| 3.4 | Add spaCy model download to Dockerfile | `Dockerfile` | `RUN python -m spacy download xx_ent_wiki_sm` after pip install |
| 3.5 | Create `analysis/ner.py` | `analysis/ner.py` | Module exists with functions listed below |
| 3.5a | — `load_cache()` | | Returns `dict` from `entities_cache.json`, empty dict if missing |
| 3.5b | — `save_cache(cache)` | | Writes `entities_cache.json` atomically |
| 3.5c | — `normalize_entity(name)` | | Lowercase, strip diacritics, collapse whitespace |
| 3.5d | — `build_regex_patterns(cache)` | | Returns compiled regex patterns for all cached entities |
| 3.5e | — `regex_scan(chunks, patterns)` | | Returns `dict[normalized_name, list[chunk_indices]]` |
| 3.5f | — `spacy_extract(chunks, already_matched)` | | Runs spaCy on chunks NOT matched by regex. Returns new entities |
| 3.5g | — `deduplicate(entities)` | | Merge by normalized name, substring, Levenshtein |
| 3.5h | — `summarize_entity(entity, chunks)` | | Ollama 2-3 sentence summary. Reuse condense.py pattern |
| 3.5i | — `generate_entity_notes(entities, output_dir)` | | Write per-entity markdown + `_entity-index.md` |
| 3.5j | — `extract_entities(result, items, on_status)` | | Main entry point. Orchestrates all above steps. Returns `list[Entity]` |
| 3.6 | Add NER step to `run.py` | `run.py` | After condense, before report. Guarded by `config.NER_ENABLED` |
| 3.7 | Add entity section to report | `report.py` | REPORT.md includes entity count + top entities table |
| 3.8 | Verify: run pipeline | Terminal | `entities/` folder created with at least 1 entity note |
| 3.9 | Verify: cache works | Terminal | Second run skips spaCy for known entities, uses regex |
| 3.10 | Verify: entity notes | File check | Notes have valid frontmatter, summary, cluster table, source files |

### Gotchas

- **spaCy model size**: `xx_ent_wiki_sm` is ~15MB, `en_core_web_sm` is ~12MB but English-only. The content is mixed PL+EN; `xx_ent_wiki_sm` handles multilingual better.
- **Ollama rate limiting**: Don't fire all entity summaries in parallel. Use sequential calls like `condense.py` does.
- **Existing `python-Levenshtein`**: Already in `requirements.txt` — reuse for fuzzy dedup.
- **Entity types**: spaCy labels differ from our output types. Map: `PER/PERSON → person`, `ORG → organization`, `GPE/LOC → location`, `PRODUCT → tool`, `WORK_OF_ART → project`.
- **Short entity names**: Filter out single-character entities and common words (stop words).
- **Cache file location**: `data/entities_cache.json` — persisted in Docker volume, survives container rebuilds.

### Performance Estimate

- **Regex scan**: Fast, ~1-2 seconds for 8000+ chunks
- **spaCy extraction**: ~30-60 seconds for 8000 chunks (first run, no cache)
- **Ollama summaries**: ~1-2 min per entity × N entities. If 50 entities → ~50-100 min. Consider batching or `NER_MIN_MENTIONS` filter
- **Subsequent runs**: Regex handles known entities instantly. spaCy only runs on genuinely new chunks

---

## Feature 4: jointhubs-os Agent

### Goal

Create a VS Code Copilot agent specialized in deep work sessions with the jointhubs-os repository. The agent understands the repo structure, manages knowledge across notes, and maintains context between sessions.

### Agent Definition File

**Path**: `.github/agents/jointhubs-os.agent.md`

### Agent Capabilities

| Capability | Description |
|-----------|-------------|
| **Repo awareness** | Knows full structure: Second Brain, agents, skills, instructions, automation |
| **Multi-source data** | Understands 3 note sources: Second Brain (repo), Obsidian Vault (separate, optional), Wispr Flow (dictation, optional) |
| **Graphify navigation** | Reads `graphify-out/GRAPH_REPORT.md` for entity-relationship context per project |
| **ThoughtMap MCP** | Uses `search_thoughts`, `list_clusters`, `get_cluster` for semantic search |
| **Knowledge management** | Decides: update existing note vs create new one. Maintains wikilinks between notes |
| **Review awareness** | Checks daily reviews (`Personal/daily/`), weekly reviews (`Operations/weekly-reviews/`), project CONTEXT.md |
| **Contact awareness** | Cross-references `peers/` with NER-discovered entities |
| **Session continuity** | Reads daily log at session start, logs insights at session end |

### Session Workflow

```
1. Session Start
   ├── Read today's daily note (if exists)
   ├── Check last 2-3 daily reviews
   ├── Check last weekly review
   └── Ask user: "What are we working on today?"

2. Context Loading
   ├── User says: "pracujmy nad fenix"
   ├── Read: fenix/CONTEXT.md
   ├── Read: fenix/graphify-out/GRAPH_REPORT.md
   ├── Search ThoughtMap: search_thoughts("fenix")
   └── Present: key state, open questions, recent activity

3. Deep Work
   ├── Answer questions from knowledge base
   ├── Find cross-project connections
   ├── Surface relevant notes user may have forgotten
   └── Propose: "This relates to note X — should I link it?"

4. Knowledge Capture
   ├── Update project CONTEXT.md if decisions made
   ├── Create new notes for topics that grew > 3 paragraphs
   ├── Add wikilinks between related notes
   └── Propose daily log entry

5. Contact Management (when people mentioned)
   ├── Check peers/ for existing info
   ├── Check entities/person/ for NER-discovered context
   └── Suggest updates if new info learned

6. Session End
   ├── Summarize decisions and insights
   ├── Suggest daily log additions
   └── Propose tomorrow's focus
```

### Tools

```yaml
tools:
  - vscode          # File operations, workspace awareness
  - execute         # Run scripts, CLI commands
  - read            # File reading
  - edit            # File editing
  - search          # Semantic and text search
  - agent           # Delegate to sub-agents (Tech Lead, Planner, etc.)
  - thoughtmap/*    # ThoughtMap MCP (search_thoughts, list_clusters, etc.)
  - todo            # Task management
```

### Skills to Reference

- `.github/skills/obsidian-vault/` — Vault conventions
- `.github/skills/obsidian-markdown/` — Markdown syntax
- `.github/skills/project-context/` — CONTEXT.md lifecycle
- `.github/skills/daily-log/` — Daily log format
- `.github/skills/weekly-review/` — Weekly review process
- `.github/skills/thoughtmap/` — ThoughtMap pipeline and MCP tools
- `.github/skills/agentic-engineering/` — System architecture

### Handoffs

| To | When |
|----|------|
| **Tech Lead** | Implementation work, debugging, code architecture |
| **Planner** | Day/week planning, prioritization |
| **Journal** | Deep reflection, pattern synthesis |
| **Investor** | Financial analysis, stock research |
| **Agent M** | Need Mateusz's voice/perspective for decisions |

### Tasks

| # | Task | File(s) | Acceptance Criteria |
|---|------|---------|-------------------|
| 4.1 | Create agent file | `.github/agents/jointhubs-os.agent.md` | Valid YAML frontmatter + full personality + workflow sections |
| 4.2 | Create ThoughtMap instructions | `.github/instructions/thoughtmap.instructions.md` | `applyTo: Second Brain/Projects/thoughtmap/**`, import conventions documented |
| 4.3 | Update assistant.instructions.md | `.github/instructions/assistant.instructions.md` | Mention ThoughtMap data sources (Obsidian Vault, Wispr Flow as optional) |
| 4.4 | Verify: agent loads in Copilot | VS Code | Agent appears in Copilot Chat agent list, responds to context queries |

---

## Feature 5: Contact Discovery (NER-driven)

### Goal

Let the NER pipeline (Feature 3) automatically discover person entities. The `peers/` directory stays unchanged — agents cross-reference both sources.

### Approach

- **No migration** — `peers/` stays as-is with manually maintained contact notes
- **NER pipeline** generates `entities/person/` automatically from ALL chunks
- **jointhubs-os agent** cross-references both: `peers/` (manual) + `entities/person/` (auto-discovered)
- Over time, NER entities become richer than hand-maintained data

### Prerequisites

- Feature 3 (NER) must be complete
- Feature 4 (agent) must know about both directories

### Tasks

| # | Task | File(s) | Acceptance Criteria |
|---|------|---------|-------------------|
| 5.1 | Verify peers/ in extraction scope | `core/extract.py`, `config.py` | `peers/` is NOT in `SECOND_BRAIN_EXCLUDE_DIRS` |
| 5.2 | Verify NER person entities | `entities/person/` | At least some person entities generated from pipeline |
| 5.3 | Agent cross-reference instructions | `.github/agents/jointhubs-os.agent.md` | Agent knows to check both `peers/` and `entities/person/` |
| 5.4 | Verify: entity note links to source | Entity markdown | `Source Files` section includes peer note paths when applicable |

---

## Implementation Order

```
Feature 1 (Folder Reorg) ──→ Feature 3 (NER) ──→ Feature 5 (Contacts)
                         ╲                     ╱
Feature 2 (README)        ╲──→ Feature 4 (Agent)
```

**Recommended sequence**:
1. **Feature 1** first — establishes import conventions, unblocks Feature 3
2. **Feature 2** in parallel — independent, can be done anytime
3. **Feature 3** after Feature 1 — needs `analysis/ner.py` in new structure
4. **Feature 4** after Features 1-2 — needs to reference final structure
5. **Feature 5** after Features 3-4 — verification only, depends on NER output + agent

### Time Estimates (approximate)

| Feature | Effort | Bottleneck |
|---------|--------|------------|
| 1. Folder Reorg | 2-3 hours | Careful import updates + testing |
| 2. README | 30 min | Copywriting |
| 3. NER | 4-6 hours | `ner.py` implementation + Ollama prompt tuning |
| 4. Agent | 1-2 hours | Agent personality + workflow design |
| 5. Contacts | 30 min | Verification only |

---

## Verification Checklist

### After Feature 1
- [ ] `docker compose up -d --build` — container builds successfully
- [ ] Pipeline runs: `Invoke-RestMethod http://localhost:8585/api/status` → `phase: done`
- [ ] Graph renders at `http://localhost:8585/`
- [ ] Import test: `python -c "from thoughtmap.core.extract import extract_all; from thoughtmap.analysis.condense import condense; from thoughtmap.web.server import serve; print('OK')"`
- [ ] `git status` shows renames, not delete+create

### After Feature 3
- [ ] `entities/` directory created in `thoughtmap-out/`
- [ ] At least 1 person, 1 org, 1 project entity discovered
- [ ] `entities.json` is valid JSON with all entities
- [ ] `_entity-index.md` has summary table
- [ ] Individual entity notes have valid frontmatter
- [ ] `data/entities_cache.json` exists after first run
- [ ] Second pipeline run: spaCy skipped for cached entities (check logs)
- [ ] REPORT.md includes entity summary section

### After Feature 4
- [ ] Agent appears in VS Code Copilot Chat picker
- [ ] Agent loads project context when asked "co wiesz o fenix?"
- [ ] Agent references graphify output
- [ ] Agent uses ThoughtMap MCP search
- [ ] Agent checks daily/weekly reviews at session start

### After Feature 5
- [ ] Agent cross-references `peers/` with `entities/person/`
- [ ] NER discovers at least some names present in `peers/` independently
- [ ] `peers/` directory unchanged (no files moved or deleted)

---

## Appendix: Existing Code Patterns to Follow

### Ollama Call Pattern (from `condense.py`)

```python
resp = requests.post(
    f"{config.OLLAMA_BASE_URL}/api/generate",
    json={
        "model": config.CONDENSE_MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.3, "num_predict": 200},
    },
    timeout=120,
)
resp.raise_for_status()
return resp.json().get("response", "").strip()
```

### Status Callback Pattern (from `run.py`)

```python
def status(msg: str):
    print(msg)
    if on_status:
        on_status(msg)

status("[8/9] Extracting named entities...")
```

### Pipeline Step Pattern (from `run.py`)

```python
# ─── Step N: NER ───
if config.NER_ENABLED:
    status(f"[{step}/{total}] Extracting named entities...")
    t0 = time.time()
    entities = extract_entities(result, items, on_status=status)
    status(f"  Found {len(entities)} entities in {time.time() - t0:.1f}s")
else:
    status(f"[{step}/{total}] NER disabled — skipping")
    entities = []
```

### TextSegment / Chunk Dataclass Pattern

```python
@dataclass
class Entity:
    name: str
    type: str
    aliases: list[str]
    normalized: str
    cluster_ids: list[int]
    source_files: list[str]
    mention_count: int
    summary: str
    first_seen: str
```
