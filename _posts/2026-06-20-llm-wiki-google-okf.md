---
layout: post
title: "Wiki-Skills gaining traction, now with Google's OKF standard"
categories: [AI Coding, LLMs, Claude Code, Agent Skill, Wiki-Skills]
excerpt: Two months after Karpathy's LLM-wiki gist, there are 200+ implementations and a Google spec. Both vindicate the bet Wiki-Skills made — pure markdown, no database — and point to a handful of improvements now folded into the Wiki-Skills.
---

TL;DR

- Andrej Karpathy described his approach to local, markdown-based agentic memory in his [LLM-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Two months and 800+ responses later, Google formalized it in a spec: the [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/).
- I created [wiki-skills](https://github.com/kfchou/wiki-skills) based on a specific gut-feeling: agentic memory can be effectively implemented in a database-less, pure markdown manner, maintained by the agent's existing tools. Faithful implementations of LLM-wiki and Google's OKF both independently arrived at the same constraints.
- There are roughly 200+ variations of the LLM-wiki implementations so far. The implementations that stayed faithful to plain markdown converged on a short list of improvements worth adopting: **claim-level provenance, contradiction flags, generated indexes, and concept de-duplication**. These are incorporated into wiki-skills as `wiki-audit`, improvements to `wiki-lint`, and automated index and log generation during wiki-query.
- The most common issue discussed in the 800+ responses is the scalability of the llm-wiki. I discuss potential solutions to be added to wiki-skills.

## Historical Context

A conclusion I drew after researching [agentic memory systems](https://kfchou.github.io/repo-memory/) was a preference towards human-readable, local, easily auditable solutions. At the time, no solution like this existed. I deliberately wanted to avoid MCP servers, vector databases, or external services, and to rely solely on agent skills.

Shortly after, in April 2026, Karpathy published a gist describing an LLM-maintained personal wiki: raw sources stay immutable, the LLM compiles them into a flat collection of interlinked markdown pages, and you query that wiki instead of re-running RAG over the raw documents on every question. I [packaged](https://kfchou.github.io/wiki-skills/) this workflow into a set of Claude Code skills — [wiki-skills](https://github.com/kfchou/wiki-skills).

There are now 800+ comments on the original gist and 200+ distinct implementations. Some implementations stayed faithful to the core tenets of llm-wiki, while others advertised their own memory/context management solutions, all involving additional infrastructure. Out of the former, many made changes outside of the original llm-wiki spec, and it's worth examining how they tackle potential shortcomings of the original spec.

## Google Backs the Wiki format with the Open Knowledge Format proposal

In June 2026, Google published the [Open Knowledge Format (OKF)](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/), an open spec that formalizes the llm-wiki pattern -- evidence that the wiki-skills direction isn't just my delusional mind hallucinating nonsense.

OKF v0.1 "represents knowledge as a directory of markdown files with YAML frontmatter.":

> Just markdown — readable in any editor, renderable on GitHub, indexable by any search tool. Just files — shippable as a tarball, hostable in any git repo, mountable on any filesystem. Just YAML frontmatter — for the small set of structured fields that need to be queryable.

And the design principle underneath it:

> The answer to [the interoperability] problem isn't another knowledge service. You need a format… a way to represent knowledge that lives in version control alongside the code it describes.

i.e., they're proposing a common format standard for llm-wiki's frontmatter to reduce siloing and increase interoperability. Both are very important to prevent the "works on my machine" problem.

This is a novel point, and a valuable addition. Of the 200+ community implementations of llm-wiki, the most common "improvement" was to add infrastructure to what the llm-wiki pattern deliberately omits: SQLite indexes (`mpazik/binder`), MCP servers and dashboards (`anzal1/quicky-wiki`, [`basicmachines-co/basic-memory`](https://github.com/basicmachines-co/basic-memory) at 3.3k⭐), typed JSON contracts (`manavgup/wikimind`), web UIs (`Hosuke/llmbase`). None of these "improvements" pushes the llm-wiki format forward or improves it in a way that is faithful to the original proposal's spirit.

## Improving on Wiki-Skills
The faithful implementations of llm-wiki do add new features not described in the original spec, which are worth learning from. After using wiki-skills for my own personal wiki, code documentation, and collaborative research projects, I've also noticed the same shortcomings and made similar improvements:

### 1. Claim and citation auditing

Claims and citations need to be audited, because LLMs still default to lazy mode -- knowledge retrieval from their own learned data -- and hallucinate.

This is a huge problem noticed by the AI dev community. Karpathy's gist already asks the LLM to note "where new data contradicts old claims," and the lint pass already hunts for contradictions. What neither does is *pin a claim to its source*. The two most mature faithful implementations both added this independently:

- **Line-range provenance.** [`atomicstrata/llm-wiki-compiler`](https://github.com/atomicstrata/llm-wiki-compiler) (1.5k⭐, the most-starred faithful fork) emits inline `^[paper.md:42-58]` citations tracing each claim to exact source lines. Cheap to write at ingest, and it turns the audit step into a lookup instead of a re-read.
- **A review gate.** The same project added `compile --review`, so a generated page can be approved or rejected before it lands in the wiki.
- **Adversarial, cross-model review.** [`axoviq-ai/synthadoc`](https://github.com/axoviq-ai/synthadoc) (471⭐) runs the contradiction check with a *second LLM from a different provider*, looking for overreach and unsupported generalizations; warnings surface in the lint output and in page frontmatter. Self-review under-catches. Cross-model review is where it found the problems.

Takeaway for `wiki-skills`: add line-range provenance to ingested claims, and make `wiki-lint`'s strong form a cross-model pass. This is implemented as `wiki-audit`.

### 2. Dynamic index and log generation

The goal of the wiki index is to **help LLMs progressively discover relevant context**. But the index just contains short summaries and tags found in the markdown frontmatter anyway. Having both frontmatters and indices is redundant. Indices also increase review friction by introducing conflicts when the wiki is being edited by multiple contributors in different branches. For all these reasons, the indices should just be auto-generated based on the markdown frontmatters of each page during runtime.

The log file suffers from similar issues; User [`aakarim`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6085832#gistcomment-6085832) pointed out that "...having a log locally only confuses less intelligent models." User [`gowtham0992`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6157839#gistcomment-6157839) had to add *log rotation* because the file grows unbounded, which is the tell that it's the wrong shape for the job.

For these reasons, logs should be autogenerated at runtime via git commit messages. **To facilitate this, OKF should also introduce wiki-specific commit message conventions**.

Takeaway for `wiki-skills`: Agent-maintained indices and logs are bloat - when working with a coding CLI and git, these files can be autogenerated at runtime. This reduces friction during reviews in collaborative projects. What we should do instead:
  * Indices should be built into the wiki front-matter
  * Specify conventions for your git commit to produce useful logging info

### 3. Concept Identity

When the LLM invents cross-links at compile time, it can hallucinate targets that don't exist. User [`manavgup`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6088113#gistcomment-6088113) says, "related titles at compile time hallucinate 404s; they have to be resolved against the existing article set at write time, not at render time. Obsidian makes this look free; it isn't." [`kytmanov/synto`](https://github.com/kytmanov/synto) (150⭐) fixes this by giving every concept a stable `entity_id` separate from its display name, so homonyms stop colliding, with `merge`/`split` commands to steer the graph. User [`peas`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6079483#gistcomment-6079483) solved it from the other side — make cross-links *mechanical* (title matching, slug patterns, co-occurrence) rather than LLM-generated, so the `[[wikilink]]` graph is trustworthy by construction.

Takeaway for wiki-skills: reviews need to audit [[wikilinks]] to ensure they're targeting the correct page.

## The Issue of Scale
### Index page
index.md-based navigation works well at small scale and breaks somewhere in the low hundreds of pages, for three distinct reasons people named separately:

- The index overflows the context window. "the query step relies on the LLM reading index.md… works at ~100 pages but breaks when the wiki grows to thousands of entries, since index.md itself overflows the context window." - [singularityjason](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6085264#gistcomment-6085264)
- You can't query by reading files anymore. "Once you're past a few hundred pages you want to ask your wiki things… You can't do that by reading files. The index helps early on but it doesn't scale." - [mpazik](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6079689#gistcomment-6079689)
- grep gets slow. "at under 50 docs the wiki alone is enough. The [search] layer earns its keep at 500+ docs when grep gets slow." - [tashisleepy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6081913#gistcomment-6081913)

At this scale, the easiest solution is to add a retrieval layer, and most people opt to use databases. However, two users suggested solutions that aligns with my own thinking:
- Token-budgeted, tiered indexes — [bluewater8008](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6079549#gistcomment-6079549): "Give the index a token budget. L0 (~200 tokens, every session), L1 (~1-2K, the index at session start), L2 (~2-5K)…" — progressive disclosure instead of one flat index.
- Sharded/nested indexes — [quenio](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6082524#gistcomment-6082524): index files "on the top-level or in any subfolder, to help scaling to a larger number of files."

My implementation for wiki-skills: 
1. The index generation needs to be adaptive -- depending on the user intent or prompt, the generation process should quickly generate a subset of index of potentially relevant articles.
2. How might "potentially relevant" be determined? This would depend on the markdown frontmatter containing rich yet parsable metadata to facilitate the index generation process.
3. Along the same lines, a flat-directory containing all wiki pages should be discouraged to facilitate the ease of index generation. 
4. How should subdirectories be structured? One methodology is to divide wiki docs among high level, commonly used, non-overlapping concepts. If no such concepts can be determined at the onset, perhaps an ontology learning procedure can be used once the wiki size has grown past a few hundred pages.

### Linting
The original llm-wiki spec calls for an audit which conducts a full health-check across the entire wiki for contradictions. As the wiki grows, this process will nuke your context window and get expensive fast. Auditing and linting needs to be implemented in smaller steps as the wiki gets updated. A few things are necessary to achieve this:
1. **Per-source contradiction detection at ingest time**. Every source ingest triggers an audit. Model only loads the pages touched during source ingestion, not the whole repository. 
One implementation is to classify a detected contradiction into one of three severities — soft, scope-mismatch, or hard (and "none" when there is no conflict). Soft and scope-mismatch are non-blocking: they get flagged, referenced, compared and explained, and you could permit them since they can be useful in setting the subject matter's peripheral context. You would also have a mechanism to keep an eye on soft/scope contradictions so they do not quietly accumulate over time without any review. Hard contradictions are not acceptable — they stop the ingestion run, hold the commit, send a notification, and block continuation of ingestion until the user manually resolves them (with an explanation of the resolution) inside the MD files. Each flagged contradiction carries a machine-readable severity token plus a status line, e.g.:
    ```text
    Contradiction severity: hard
    Status: Unresolved — flagged for user review
    ```
2. **Pre-commit gates**. Deterministically block commits if a "Status: Unresolved" exists on yaml frontmatters in the staged files. Flagging these files is a fast and deterministic process, easily done with a python script.

3. **The periodic lint backstop**. Loads all pages marked to be contradicting for review. If steps 1 and 2 are done correctly, this should no longer nuke your context window.

### Summary - Tackling Scale
> The scale issue can't be tackled by LLMs alone. Instead, we address it by setting up good software engineering process around it in conjunction with lightweight LLM models.

While many gravitate toward implementing actual databases to tackle scale, I still prefer markdown-only approaches, supported by simple scripts. These can be summarized by:
1. Setting up git and git hooks to run scripts
2. Determining a rich and parsable markdown frontmatter format to support the above scripts

Implementing these simple processes have already enhanced my experience with using the llm-wiki system for both solo and collaborative projects. I'm excited to see how the llm-wiki ecosystem will continue to evolve from here.

## Projects referenced

Faithful to the markdown-only, agent-native constraints (star counts as of June 2026):

- [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) — 1.5k⭐ — claim provenance, `compile --review`, confidence/contradiction metadata
- [xoai/sage-wiki](https://github.com/xoai/sage-wiki) — 540⭐ — single Go binary, compiles sources into an Obsidian vault with wikilinks + frontmatter
- [axoviq-ai/synthadoc](https://github.com/axoviq-ai/synthadoc) — 471⭐ — adversarial cross-model review, claim-level provenance
- [kytmanov/synto](https://github.com/kytmanov/synto) — 150⭐ — concept identity, homonym handling, `merge`/`split`
- [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — 157⭐ — the Claude Code skill set this post feeds back into
- [rarce/git-wiki](https://github.com/rarce/git-wiki) — 20⭐ — remote git repo as canonical store, "diffs as a change log"
- [pumblus/okf-harness](https://github.com/pumblus/okf-harness) — Open Knowledge Format-compatible markdown with a JSON CLI contract for agents

## Further reading

- [The original LLM-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Karpathy, April 2026
- [Google's Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/) and the [knowledge-catalog project](https://github.com/GoogleCloudPlatform/knowledge-catalog)
- [Introducing Wiki-Skills](https://kfchou.github.io/wiki-skills/) — my first post on this pattern
- [Why grep beat embeddings](https://jxnl.co/writing/2025/09/11/why-grep-beat-embeddings-in-our-swe-bench-agent-lessons-from-augment/) — the case for plain-text retrieval in coding agents
