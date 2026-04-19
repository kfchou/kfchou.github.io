---
layout: post
title: "Introducting Wiki-Skills: Agent Skill for Managing Markdown Vaults"
categories: [AI Coding, LLMs, Claude Code, Agent Skill]
excerpt: Kaparthy shared a viral note about a building an LLM-managed 'personal wiki' - which I interpret as a specific instance of a locally stored markdown vault. Here, I present Wiki Skills - a set of agentic Skills that captures the process of creating, querying, and updating this knowledge vault. 
pinned: true
---

TL;DR: Andrej Karpathy described an LLM-maintained personal wiki — I see this as a specific instance of the local markdown vault pattern. [wiki-skills](https://github.com/kfchou/wiki-skills) is a set of Claude Code skills that implements it.

- The vault pattern — a directory of interlinked markdown files you own and extend over time — is already familiar to Obsidian users; Karpathy showed how an LLM can maintain one on your behalf
- wiki-skills packages this as five skills: init, ingest, query, lint, update — no MCPs, no databases, just the agent's existing tools and markdown files
- The pattern is general-purpose; one particularly good application is repo memory — the institutional knowledge a coding agent needs between sessions
- The skills are a starting point; modify them to fit your domain and workflow

## The Local Markdown Vault

Obsidian built a large user base around a simple idea: a local directory of interlinked markdown files — a *vault* — that you own, navigate, and extend over time. Simple, lightweight, free and private.

In April 2026, Andrej Karpathy published [an idea about a personal knowledge base workflow](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) that went viral: 5,000+ stars and 3,500+ forks within a week. The main idea:

1. Source documents go into a `raw/` directory — untouched, as ingested
2. An LLM synthesizes a wiki from those sources — a flat collection of markdown pages, cross-referenced and indexed
3. You query the wiki by asking an LLM questions against it

Karpathy didn't frame this as a markdown vault. But that's how I read it: the compiled wiki layer is exactly the kind of interlinked markdown structure Obsidian users already work with. The difference is who does the maintenance. Maintaining a wiki is impractical for humans because cross-referencing and keeping summaries current is tedious. On the othe hand, LLMs don't get bored, don't forget to update a backlink, and can touch 15 files in one pass. Let LLM take care of the boring stuff, so you get to do the interesting stuff.

The result is a persistent, compounding artifact. Unlike RAG — where the LLM rediscovers knowledge from raw documents on every query — the wiki accumulates. Every ingest enriches it. Every question you ask can be filed back as a new page. The longer you use it, the more useful it gets.

## Wiki-Skills

I created [wiki-skills](https://github.com/kfchou/wiki-skills) to package this pattern as a set of Claude Code skills — no MCP servers, no vector databases, no external services. The agent uses its existing tools (`Read`, `Write`, `Grep`, glob patterns) to build and maintain the wiki.

### General-purpose by Design

Wiki-skills is not a codebase-specific tool. It works for any domain where knowledge accumulates over time: research papers, reading notes, competitive analysis, personal knowledge, or codebase documentation. The domain is configured at init time — `wiki-init` asks what the domain is, what kinds of sources you'll add, and what index categories to use. Domain-specific defaults are built in:

- Research: `Sources | Entities | Concepts | Analyses`
- Codebase: `Modules | APIs | Decisions | Flows`

Everything flows from `SCHEMA.md`, a configuration file at the wiki root that records domain, source types, page frontmatter format, and index taxonomy. Every skill searches for it from the current directory upward — it's what makes the skills stateless and composable across sessions. As conventions emerge, you and the agent co-evolve SCHEMA.md. The skill files themselves are plain markdown describing workflows, so you can modify those too for deeper changes.

### How the Five Skills Work

**wiki-init** bootstraps the three-layer structure: `raw/` for immutable source documents, `wiki/` for LLM-maintained pages (flat `pages/` directory, `index.md`, `overview.md`, `log.md`), and `SCHEMA.md` at the root.

**wiki-ingest** is the most involved. Before writing anything, it surfaces key takeaways and asks what to emphasize. Then it writes a source summary page, updates any entity or concept pages the source touches, and runs a backlink audit — scanning every existing page for unlinked mentions of the new entities and adding `[[slug]]` references where missing. The skill file calls this "the step most commonly skipped" and the one where compounding value comes from. One ingest typically touches 10–15 pages.

**wiki-query** is explicitly forbidden from answering from general knowledge — it must read the wiki first, even when it thinks it knows the answer. It synthesizes a response with inline `[[slug]]` citations, then always offers to file the answer back as a new wiki page. This is the other half of the compounding loop: the wiki grows from both ingests *and* queries.

**wiki-lint** runs a severity-tiered audit: 🔴 errors (broken links, missing frontmatter), 🟡 warnings (orphan pages, contradictions, stale claims), 🔵 info (missing concept pages, coverage gaps). It always writes a lint report without asking, and always shows diffs before applying fixes.

**wiki-update** revises existing pages. Every change requires a cited source. After updating, it greps for all pages that link to the changed page and flags downstream effects, then sweeps for the same stale claim across the full wiki.

> **Try it yourself**: Install wiki-skills from the [repo](https://github.com/kfchou/wiki-skills), then run `/wiki-init` in Claude Code. The init walk-through asks four questions and takes about two minutes. Then run `/wiki-ingest` on any document — a paper, a URL, or a local file.

## Getting Started

If you're already using Claude Code:

1. Install wiki-skills: follow the instructions at [github.com/kfchou/wiki-skills](https://github.com/kfchou/wiki-skills)
2. Run `/wiki-init` — it asks four questions and bootstraps the structure
3. Run `/wiki-ingest` on a few sources to seed the wiki
4. Run `/wiki-query` to ask questions; save useful answers back as pages
5. Adapt the skills: change the index taxonomy, adjust page formats, add `wiki-query` calls to your existing workflow skills

The skills are a starting point, not a finished product. The goal is a wiki that reflects how your domain is actually structured — maintained by your agent, readable by you.

## Wiki-Skills for Repo Context Management

In a [previous post](https://kfchou.github.io/repo-memory/), I surveyed the landscape of agentic memory solutions: tools like Graphiti, A-MEM, Claude-mem, and Engram. Most default to databases — vector DBs, graph stores, SQLite — and my theory is that this is largely a historical accident. RAG got popular, vector DB infrastructure followed, and memory systems were built on top of what was already there.

For general agent memory across many sessions and many users, that infrastructure may be warranted. But for repo memory — the context a coding agent needs to pick up where it left off on a specific codebase — the retrieval problem is much simpler. The documents are small, the domain is bounded, and the agent can `grep`. There's [an established argument](https://jxnl.co/writing/2025/09/11/why-grep-beat-embeddings-in-our-swe-bench-agent-lessons-from-augment/) that coding agents moved away from embeddings for exactly this reason.

Repo memory is information that changes slowly, needs to be auditable by a human, and maps naturally to documents: ADRs, design notes, architectural decisions, codebase walkthroughs. A markdown vault is the right shape for this. Markdown is human-readable, git-friendly, zero infrastructure, and moves easily with the repo.

Wiki-skills fits this use case well precisely because it's general-purpose — you configure it toward your codebase rather than receiving a tool with fixed assumptions. Initialize with the codebase taxonomy (`Modules | APIs | Decisions | Flows`), ingest your existing documentation, and the wiki builds up a structured, cross-referenced picture of the codebase. New decisions get ingested as they're made. Questions get asked against the wiki and good answers get filed back.

**Closing the retrieval loop**: the wiki only helps if the agent knows to consult it. A few practical patterns:

- **Pointer in CLAUDE.md**: one line pointing to the wiki path and when to use it. The agent reads CLAUDE.md at session start.
- **Skill-level triggers**: if you have a feature-development skill, add a `wiki-query` call at the top before the agent starts coding. The skill encodes the retrieval logic.
- **Ingest on completion**: at the end of a task, run `wiki-ingest` on the ADR or session summary you just wrote. The wiki stays current without a separate maintenance pass.

Retrieval is a skill problem, not a database problem. The agent can read a 30-line index and decide which two pages are relevant to the current task.

