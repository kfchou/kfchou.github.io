---
layout: post
title: "Deep Dive into CC Source Code - Chapter 1: Memory Management"
categories: [AI Coding, LLMs, Claude Code, Wiki-Skills]
excerpt: What makes the Claude Code harness best-in-class? Let's dive into its leaked source code to learn about the rigorous engineering within. Turns out, its memory management is remarkably similar to the wiki system described in my previous post.
pinned: true
---

On March 31, 2026, Anthropic accidentally shipped the Claude Code source code — a missing `.npmignore` entry bundled a 59.8 MB source map inside npm package v2.1.88, exposing [~512,000 lines of unobfuscated TypeScript](https://www.theregister.com/2026/03/31/anthropic_claude_code_source_code/). Within hours it was mirrored across GitHub.

Massive media coverage followed:
* 187 loading spinner verbs including "hullaballooing" and "razzmatazzing," [regex-based frustration detection](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) triggered by "wtf" and "ffs"
* [18 terminal pets](https://codingbeautydev.com/blog/new-claude-code-buddy-feature/) for the buddy system
* and a [mysterious "Mythos" model](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/) that had leaked a week before in a separate incident.

But those were all noise.

I wanted to know -- what made the Claude Code harness best-in-class? In this first post of a Claude Code Harness deep-dive, we look into its memory management system. Turns out, Claude Code's memory management is [strikingly similar](#lessons-for-wiki-skills) to the [wiki-skills system](/2026/04/12/wiki-skills) I'd built separately -- they're convergent solutions to the same underlying problem: how does a context-limited agent maintain coherent state over time?

## Memory Management — Five Layers

Claude Code has five distinct memory systems, each operating at a different timescale and purpose. Understanding all five is essential for building a robust harness.

```text
Each submitMessage() call:
  1. loadMemoryPrompt() → inject relevant memdir memories (age-weighted)
  2. fetch CLAUDE.md files → inject as nested_memory attachments (dedup via loadedNestedMemoryPaths)
  3. LLM call with full context
  4. Tool calls execute (FileStateCache updated on each read)
  5. Final response → post-turn:
     a. extractMemories (forked agent, async)
     b. autoDream check (time + session + lock gates)
     c. sessionMemory update
```

## Layer 1: FileStateCache — What the Model Has Seen

**Summary.** FileStateCache is the model's working memory for files — it uses an index to track files the model has most recently read. Old reads get evicted when the cache fills up. The `isPartialView` flag and Cache Eviction both mean the model must re-read before editing, ensuring it never acts on stale or unseen content.

**File:** `src/utils/fileStateCache.ts`

An LRU cache (100 entries, 25MB max) tracking every file the model has read this session.

```typescript
export type FileState = {
  content: string
  timestamp: number
  offset: number | undefined
  limit: number | undefined
  isPartialView?: boolean  // ← the key safety flag
}
```

**The `isPartialView` flag is the most important field here.** It's set when a file was auto-injected (e.g., CLAUDE.md) but the model only saw a processed version (HTML stripped, frontmatter removed, truncated MEMORY.md). The raw disk bytes are stored in `content` for diffing, but the model never saw them.

When `isPartialView` is true, `FileEditTool` and `FileWriteTool` require an explicit `FileReadTool` call first. This prevents the model from issuing edits based on content it's never actually seen. The type system enforces it.

**What this is in plain terms.** FileStateCache is the model's reading history for a session. Every time Claude Code reads a file, that file gets logged here. The `isPartialView` flag solves a subtle correctness problem: sometimes Claude Code pre-processes a file before showing it to the model (stripping HTML, truncating long files). The raw bytes on disk differ from what the model saw. Without tracking this, the model could issue an edit against content it never actually read — silently corrupting a file. So the type system enforces: if `isPartialView` is true, you must explicitly re-read the file before editing it.

**Path normalization.** All keys are `normalize()`d before storage — relative paths, `..` segments, and mixed separators all resolve to the same cache key. This prevents cache misses from cosmetic path differences.

**Takeaway:** Auto-injection creates a gap between what's on disk and what the model has seen. That gap must be tracked explicitly — without it, the system cannot know which files are safe to edit and which require a re-read first.

## Layer 2: memdir — Persistent Semantic Memory

**Summary.** memdir is where memories survive across sessions. It's distinct from CLAUDE.md: CLAUDE.md is static instruction ("what to do"), memdir is dynamically extracted memory ("what was true"). On each query, Sonnet selects up to 5 relevant memories from a metadata manifest — cheap to score, precise to load. Age doesn't filter memories out; it modulates trust. Old memories still get loaded but with a staleness caveat, preventing stale context from silently overriding recent reality while not discarding potentially useful history.

**Files:** `src/memdir/`

The `memdir` system is a file-based persistent memory directory at `~/.claude/projects/<path>/memory/`. It has semantic structure:

- `findRelevantMemories.ts` — LLM-based relevance scoring via `sideQuery()` (Claude Sonnet)
- `memoryScan.ts` — scans memory directory, extracts frontmatter metadata (up to 200 files), sorts newest-first
- `memoryAge.ts` — injects staleness caveat for memories >1 day old (does not filter them out)
- `memoryTypes.ts` — typed memory categories (user, feedback, project, reference)
- `paths.ts` — path resolution, `isAutoMemoryEnabled()` gate

**How relevance scoring works.** `findRelevantMemories()` calls `selectRelevantMemories()`, which sends a manifest of memory *metadata* (not full content) to Claude Sonnet via `sideQuery()`. Sonnet receives the user's query, the manifest (type + filename + timestamp + description), and recently-used tools. It selects up to 5 memories that will "clearly be useful" — selective by design. Sonnet sees the timestamps in the manifest and weighs both semantic relevance and age together. Full content is only loaded for the selected entries. This is progressive discovery: tiny tokens to score, targeted load.

**Why descriptions matter.** Sonnet reads the one-line description in each memory's frontmatter to decide relevance. A vague description ("some user info") won't score well. Precise descriptions ("user prefers TypeScript, switched from Python in April 2026") score correctly.

Memories are loaded at query time via `loadMemoryPrompt()` in `QueryEngine.ts`. The system prefetches relevant memories during parallel startup and injects them as context.

**Auto-memory vs CLAUDE.md.** CLAUDE.md is project-level instruction. memdir is project-specific *extracted* memories from past sessions. They're injected differently and serve different purposes.

**Takeaway:** Progressively discover relevant context — maintain a cheap, scannable index with precise descriptions, then load full content only after relevance is confirmed. Keep descriptions specific; vague metadata degrades selection silently. Age modulates trust, not access.

**Interpretation:** memdir's architecture is structurally identical to a well-organized wiki:

| memdir | Wiki |
|--------|------|
| `MEMORY.md` index | `wiki/index.md` |
| One-line description per memory file | One-line summary per `[[page]]` |
| Sonnet scores metadata manifest to pick relevant files | Query skill scans index to find relevant pages |
| Full file loaded only when selected | Full page read only when needed |
| Cap of 5 files per query | Focused set of pages per session |
| `memoryTypes.ts` — user/feedback/project/reference | Tag system — patterns/modules/flows/decisions |

The core insight is the same: don't load everything, load the right things. Keep a cheap scannable index with precise descriptions. Load full content only after relevance is confirmed. The difference is who scores relevance — memdir uses Sonnet via `sideQuery()`, a wiki uses a human or a query skill. Claude Code essentially built a wiki for itself.

## Layer 3: extractMemories — Post-Turn Forked Agent

**File:** `src/services/extractMemories/extractMemories.ts`

After each complete query loop (model produces a final response with no tool calls), a **forked agent** runs to extract durable memories from the session transcript and write them to the memdir.

```text
main loop completes → handleStopHooks → initExtractMemories() fires
                                           ↓
                                    runForkedAgent(
                                      prompt: "extract memories from this transcript",
                                      tools: [FileRead, FileWrite, FileEdit, Glob, Grep, Bash]
                                    )
                                           ↓
                                    writes to ~/.claude/projects/.../memory/
```

Key design decisions:
- Uses `runForkedAgent()` — shares the parent's prompt cache, so extraction is nearly free at the cache layer
- Closure-scoped state (not module-level) so tests can call `initExtractMemories()` in `beforeEach` for fresh state
- Gated by `isAutoMemoryEnabled()` and GrowthBook feature flag
- Supports team memory sync (`TEAMMEM` feature flag) — memories extracted to shared team paths

**Wiki analogy.** Layer 3 maps to `/wiki-ingest` — both distill a completed unit of work into durable, structured knowledge. The difference: `extractMemories` fires automatically after every turn; `/wiki-ingest` is manual, requiring the human to decide what's worth capturing. Automatic extraction is consistent but risks noise and loss of nuance; manual extraction has higher signal but requires human in the loop (HITL). Claude Code resolves this by enforcing typed categories (`user`, `feedback`, `project`, `reference`) to filter conversational noise. Wiki resolves it with human judgment.

**Takeaway:** Memory must be continuously updated to be useful. Claude Code does this automatically, with typed categories filtering out conversation noise. Wiki updates are more free-form and requires HITL. But the process can be automated once the memory types for a use case are settled — hooks can trigger wiki updates at session end (`PostSession` hook), and the forked-subagent flow makes the extraction efficient.


## Layer 4: autoDream — Background Memory Consolidation

**Summary:** Fires a consolidation prompt to merge observations, removes contradictions, and converts vague insights into durable facts. A `DreamTask` entry tracks it in AppState so the UI can show it.

**File:** `src/services/autoDream/autoDream.ts`

Applies a three-gate pattern (time → count → lock), a standard short-circuit evaluation pattern, to resource acquisition: filter cheap conditions first, acquire expensive resources last.

```text
Time gate: hours since lastConsolidatedAt >= minHours
      ↓ (pass)
Session gate: transcript count with mtime > lastConsolidatedAt >= minSessions
      ↓ (pass)
Lock gate: no other process mid-consolidation (file lock)
      ↓ (pass)
runForkedAgent("/dream — consolidate memories")
```

A `SESSION_SCAN_INTERVAL_MS = 10 * 60 * 1000` throttle prevents rescanning too often when the time gate passes but session gate doesn't.

**Wiki analogy.** Layer 4 maps to `/wiki-lint` — both sweep for contradictions, stale content, and drift that accumulates across sessions. The difference:

| | Claude Code | Your wiki |
|---|---|---|
| **Trigger** | Automatic, idle-time | Manual `/wiki-lint` |
| **Mechanism** | LLM consolidation via `/dream` prompt | Lint report + human judgment |
| **Contradiction resolution** | Model merges and rewrites | Human decides which version wins |
| **Frequency** | After enough sessions accumulate | When you remember to run it |

Contradiction accumulation is inevitable at scale. Claude Code automates resolution at the cost of LLM judgment calls you can't audit. Your wiki keeps humans in the loop at the cost of consistency depending on discipline.

**Takeaway:** Dream runs on a timer. Wiki lint is manual. A hook or timer would keep the wiki quality high automatically.

## Layer 5: Session Memory (SessionMemory service)

**Files:** `src/services/SessionMemory/`

A within-session scratch memory separate from cross-session memdir. Used during compaction — `truncateSessionMemoryForCompact()` preserves a condensed version of the current session's memory across a compaction boundary, so the model doesn't lose the current session context entirely.

`getLastSummarizedMessageId()` / `setLastSummarizedMessageId()` tracks which messages have been folded into session memory, preventing re-summarization.


## Lessons for wiki-skills

Three of the five layer's management have a direct wiki-skill equivalent, validating the wiki system I'm experimenting with:

| Claude Code Layer | Timescale | Wiki-Skills Equivalent |
|---|---|---|
| **FileStateCache** — tracks which files the model has read and whether it saw a pre-processed view | Within a tool call | No direct equivalent; wiki doesn't gate edits on read history |
| **memdir** — persistent semantic memory, scored by relevance at query time | Across sessions | Markdown vault + `MEMORY.md` index; `/wiki-query` loads relevant pages |
| **extractMemories** — forked agent distills durable memories from the session transcript after each turn | End of turn | `/wiki-ingest` — same distillation, but manual and human-triggered |
| **autoDream** — background consolidation pass that merges contradictions and stales old facts | Idle time (multi-session) | `/wiki-lint` — same sweep, but manual |
| **SessionMemory** — within-session scratch memory preserved across compaction boundaries | Within a session | Conversation context (not persisted) |

At the same time, this deep-dive into Claude Code's memory management revealed several weakness in the current Wiki-Skills workflow. memdir has explicit guards against scale pressure that the wiki currently lacks. As the wiki grows, the same failure modes will appear at a slower timescale:

| Failure mode | memdir's guard | Wiki equivalent needed |
|---|---|---|
| Index bloat | 200 file scan cap, 5 load cap | Hard cap on index entries per category |
| Topic drift | autoDream consolidation | Scheduled `/wiki-lint` |
| Query noise | Age-weighted scoring in `findRelevantMemories` | Recency weighting in `/wiki-query` |
| Ingest redundancy | Typed categories filter noise | Contradiction sweep on every ingest |

## Why This Matters

There's a deeper implication here beyond structural similarity.

Claude is [trained on Claude Code sessions as RL signal](https://assets.anthropic.com/m/74342f2c96095771/original/Natural-emergent-misalignment-from-reward-hacking-paper.pdf). The model has been shaped by the same memory patterns — the index-then-load retrieval, the typed memory categories, the forked-agent extraction flow — that the wiki system replicates. Claude doesn't just work *with* these patterns; it has internalized them as the expected shape of a well-run agentic session.

That's not a coincidence to exploit — it's a reason the wiki system works as well as it does. When `/wiki-query` scans an index and loads only relevant pages, Claude recognizes that flow. When `/wiki-ingest` produces typed, frontmatter-structured memory files, Claude reads them fluently. The format matches what the model was trained to produce and consume.

**The wiki system isn't just inspired by the Claude Code harness; The wiki system is inherently compatible with Claude at the model level.**