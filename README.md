# Jointhubs OS

<p align="center">
  <img src=".github/assets/jointhubs.png" alt="Jointhubs" width="450">
</p>

> Multi-agent VS Code Copilot system for Obsidian + Google Workspace

**Fork this repo and make it yours.** Your brain works differently — so should your AI assistant.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      VS Code Copilot                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐  │
│  │Tech Lead│ │ Planner │ │ Journal │ │ Review  │ │  ...  │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └───┬───┘  │
│       └───────────┴───────────┴───────────┴─────────┘       │
│                           │                                  │
│              reads/writes │ daily logs                       │
│                           ▼                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Second Brain/                      │   │
│  │   Operations/ ─── Personal/ ─── Projects/            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │
         │ MCP
         ▼
  ┌──────────────────────────────┐
  │  External Services (MCP)     │
  │  Google Workspace, etc.      │
  └──────────────────────────────┘
```

Agents stay effective through **well-maintained instructions and skills** — they guide navigation, workflows, and context sharing across sessions.

## Documentation

| README | What's Inside |
|--------|---------------|
| **[Second Brain](Second%20Brain/README.md)** | Your notes — structure, conventions, customization |
| **[Operations Docs](Second%20Brain/Operations/Docs/README.md)** | Setup guides for repo init and AI development |
| **[Agents](.github/agents/README.md)** | Agent personalities and how to create your own |
| **[Skills](.github/skills/README.md)** | Domain knowledge the agents reference |
| **[Instructions](.github/instructions/README.md)** | Directory-scoped rules |

## Mechanics

- **Notes live in Second Brain** — agents read/write these files for context.
- **Skills define knowledge** — `.github/skills/*/SKILL.md` teaches agents how to work.
- **Instructions enforce rules** — `.github/instructions/` scopes behavior to directories.
- **MCP connects tools** — agents can call MCP servers (e.g., Google Workspace) to act on calendars, tasks, and email.
- **Change your structure?** Update skills + instructions so agents can still find your notes.

## Readme Index

### Core

- [Second Brain](Second%20Brain/README.md)
- [Agents](.github/agents/README.md)
- [Skills](.github/skills/README.md)
- [Instructions](.github/instructions/README.md)

### Second Brain

- [Operations](Second%20Brain/Operations/README.md)
- [Operations Docs](Second%20Brain/Operations/Docs/README.md)
- [Repo Init Docs](Second%20Brain/Operations/Docs/repo-init/README.md)
- [AI Development Docs](Second%20Brain/Operations/Docs/ai-development/README.md)
- [Periodic Notes](Second%20Brain/Operations/Periodic%20Notes/README.md)
- [Daily Notes](Second%20Brain/Operations/Periodic%20Notes/Daily/README.md)
- [Weekly Notes](Second%20Brain/Operations/Periodic%20Notes/Weekly/README.md)
- [Meetings](Second%20Brain/Operations/Meetings/README.md)
- [Personal](Second%20Brain/Personal/README.md)
- [Health](Second%20Brain/Personal/Health/README.md)
- [Finances](Second%20Brain/Personal/Finances/README.md)
- [Events](Second%20Brain/Personal/Events/README.md)
- [Classes](Second%20Brain/Personal/Classes/README.md)
- [Projects](Second%20Brain/Projects/README.md)
- [Jointhubs OS Upgrade](Second%20Brain/Projects/jointhubs-os-upgrade/README.md)

## Quick Start

1. **Fork & clone** this repo
2. **Open in Obsidian** — This repo IS your vault
3. **Configure MCP locally** — Copy `.vscode/mcp.json.example` to `.vscode/mcp.json` and add your own credentials
4. **Open VS Code** → Copilot Chat → Select agent → Start working

Detailed guides:

- **Repo setup:** [Second Brain/Operations/Docs/repo-init/README.md](Second%20Brain/Operations/Docs/repo-init/README.md)
- **AI customization:** [Second Brain/Operations/Docs/ai-development/README.md](Second%20Brain/Operations/Docs/ai-development/README.md)

### Local MCP Setup

- `.vscode/mcp.json` is for your local machine only and is ignored by git.
- `.vscode/mcp.json.example` is the safe template you can commit and share.
- If you already created `.vscode/mcp.json`, keep it locally and do not commit it.
- If the file was ever tracked by git, untrack it without deleting your local copy:

```powershell
git rm --cached .vscode/mcp.json
```

- Then keep your personal secrets only in `.vscode/mcp.json` on your machine.

## Structure

```
jointhubs-os/
├── .github/
│   ├── agents/              ← Agent personalities
│   ├── skills/              ← Domain knowledge  
│   ├── instructions/        ← Directory-scoped rules
│   └── copilot-instructions.md
├── Second Brain/            ← YOUR NOTES
│   ├── Operations/          ← Daily logs, meetings
│   ├── Personal/            ← Life tracking
│   └── Projects/            ← Active work
└── README.md
```

## The Three Layers

### 1. Agents — Who

Personalities that handle different types of work.

```
.github/agents/*.agent.md
```

| Agent | Purpose |
|-------|---------|
| **Tech Lead** | Code, architecture, debugging |
| **Designer** | UX review, interface critique |
| **Planner** | Daily/weekly planning |
| **Journal** | Reflection, patterns |
| **Review** | Weekly synthesis |
| **DeepWork** | Focus sessions |
| **Inbox** | Email triage |

### 2. Skills — What They Know

Domain knowledge agents reference when needed.

```
.github/skills/*/SKILL.md
```

Skills are **folders** with a `SKILL.md` file and optional resources (templates, examples).

### 3. Instructions — Rules By Context

Directory-scoped rules that apply automatically.

```
.github/instructions/*.instructions.md
```

Example: `projects.instructions.md` applies when working in `Second Brain/Projects/`.

## Customization Contract

**When you change your notes, update the agents.**

| You Changed | Update This |
|-------------|-------------|
| Folder paths | `.github/skills/obsidian-vault/SKILL.md` |
| Daily log format | `.github/skills/daily-log/SKILL.md` |
| Project structure | `.github/skills/project-context/SKILL.md` |
| New conventions | `.github/instructions/*.instructions.md` |

See [Second Brain README](Second%20Brain/README.md) for more on note strategies.

## License

MIT — See [LICENSE](LICENSE)

---

**Join your hubs. Ship your work.** 🧠
