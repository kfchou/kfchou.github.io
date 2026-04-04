---
layout: post
title:  "A Review on Agentic Memory"
categories: [AI Coding, LLMs, Claude Code]
excerpt: Managing context for long-running agents, across sessions, or swarms of agents, remains an active area of research and development. This is a survey of the current landscaspe in the world of Agentic memory.
---

TL;DR: Memory management for LLMs is an active research area. There are many memory solutions, each with different approach, philosophy, and amount of supporting infrastructure required.

* Enabling a single, infinite session - e.g., [Memtree](https://memtree.dev/) (B-tree context compression), [Letta](https://www.letta.com/blog/letta-code) (sleep-time reflection + skill improvement)
* Memory across sessions - Critical for agent swarms and multi-agent workflows. e.g. [Claude-mem](https://github.com/thedotmack/claude-mem) (compaction + database), [A-MEM](https://github.com/DiaaAj/A-MEM-mcp/tree/main) (self-evolving knowledge graph), [Graphiti](https://github.com/getzep/graphiti) (temporal context graphs), [Cognee](https://github.com/topoteretes/cognee) (ontology-enforced graph), [Engram](https://github.com/Harshitk-cp/engram) (confidence-weighted memory)
* Local context: Strategic `CLAUDE.md` files. e.g., [RepoAgent](https://github.com/OpenBMB/RepoAgent) (automated doc sync via pre-commit), [OpenViking](https://github.com/volcengine/OpenViking) (filesystem-based layered memory)
* Learning is simply updating of memory - e.g., [Claudest](https://github.com/gupsammy/Claudest) (extract-learnings skill), [Athena](https://github.com/winstonkoh87/Athena-Public) (goal-structured reflection), [ai-maestro](https://github.com/23blocks-OS/ai-maestro) (feedback learning loop), [context-hub-plugin](https://github.com/ScottRBK/context-hub-plugin) (API doc knowledge accumulation)

Which solution should you choose? If you're choosing a solution for a personal assistant, packages like Memtree and A-MEM may suffice. As a developer, I started thinking about this problem because Architectural Decision Records ([ADRs](https://kfchou.github.io/ADR-skill/)) serve as a type of repo memory. These ADRs need to be human readable, auditable, and easily accessed. But many solutions that require databases makes it difficult for a human to quickly retrieve and review them (Yes I believe humans are still needed in software). Relying on a vector DB for semantics + another SQL database for storage feels like unnecessary overhead and memory bloat. After all, there's [a reason](https://jxnl.co/writing/2025/09/11/why-grep-beat-embeddings-in-our-swe-bench-agent-lessons-from-augment/) why LLMs moved away from using vector embeddings, and just `grep`s your codebase instead. An ideal memory system for me would keep documents like ADRs in human readable form (e.g., markdown files). So I personally gravitate towards a solution that only uses local context.

Edit April 2026: Added [Local Indices](#local-indices) section

---

In the very early days, devs stuffed their primary memory file (CLAUDE.md or AGENTS.md) with everything to "make an agent smarter", and quickly learned that this pattern is poor practice. By 2026 it is commonly known that **CLAUDE.md files need to be kept lean** to avoid cluttering your context window. In "[Agentic Code Development with Claude Code](https://kfchou.github.io/agentic-coding/)", I wrote about how the use of subagents is another reason why a lean memory file is important. This begs the question, _how_ should we manage the repo history and memory for long-running tasks? What if the task required multiple sub-agents agents and handoffs? This review is a survey of the current solution landscsape to agentic memory.

- [Long-running Single Session Memory](#long-running-single-session-memory)
  - [Memtree (closed source)](#memtree-closed-source)
  - [Letta (21,582 ★)](#letta-21582-)
- [Memory Across Sessions (Memory Persistence)](#memory-across-sessions-memory-persistence)
  - [Claude-mem (35,468 ★)](#claude-mem-35468-)
  - [A-MEM (886 ★)](#a-mem-886-)
  - [Graphiti (23,766 ★)](#graphiti-23766-)
  - [Cognee (13,843 ★)](#cognee-13843-)
  - [Engram (15 ★)](#engram-15-)
- [Local context](#local-context)
  - [Strategically placed CLAUDE.md files](#strategically-placed-claudemd-files)
  - [Local Indices](#local-indices)
  - [RepoAgent (920 ★)](#repoagent-920-)
  - [OpenViking (12,105 ★)](#openviking-12105-)
- [Learning and Memory](#learning-and-memory)
  - [Active Learning as a Skill Pattern](#active-learning-as-a-skill-pattern)
- [Honorable mentions](#honorable-mentions)
- [Further Reading](#further-reading)


## Long-running Single Session Memory
[OpenClaw](https://github.com/openclaw/openclaw) has been making waves in the past two months. Under the hood, its essentially a long-running Claude agent that is always on. It has an orchestrator for model routing and integrations with everyday communication apps. There's currently a [shortage of Mac Minis](https://www.scmp.com/tech/tech-trends/article/3346538/apples-mac-mini-selling-out-across-china-openclaw-fever-rages) in China due to its popularity. A long-running agent like OpenClaw needs some kind of memory system to overcome [context rot](https://research.trychroma.com/context-rot). So projects like [Memtree](https://memtree.dev/) have popped up to support long-running agents.

### [Memtree](https://memtree.dev/) (closed source)

In Memtree, context Memory is structured as a B-tree where the top of the tree contains a high level summary of the current message history and the bottom of the tree contains verbatim excerpts from that history that are relevant to recent messages. In between are summaries that get more detailed as you go towards the leaves. Rather than simply return matching chunks of text without context, as is typical with RAG, they retrieve relevant details contextualized within a tree of summaries. It's a specialized form of GraphRAG where relationships between nodes are encoded in the tree structure. This tree structure allows us to efficiently expand and collapse nodes based on relevance at query-time. ([how it works](https://api.polychat.co/context-memory#how-it-works))

Memtree is the backend of [Claude Code Infinite](https://github.com/crizCraig/claude-code-infinite), where your current sessions context would actually decrease as your session continues. This is achieved by **compressing your current context using memtree** in the backend. If you often require long-running sessions, then Claude Code Infinite would appear to be a nice solution.

### [Letta](https://github.com/letta-ai/letta) (21,582 ★)

Letta is a coding harness. It is designed around long-lived agents that persist across sessions and improve with use. This is accomplished by supporting long-running memories and improved skill-use over time (learning skills as you go).

Letta uses specific repositories to store context. The [context repo](https://www.letta.com/blog/context-repositories#:~:text=Memory%20repositories%20are%20agnostic%20to,enable%20it%20for%20existing%20agents.) contains yaml files with frontmatter similar to skill files. It then uses progressive disclosure to feed these memories to your agent as needed.

Learning, skill improvement, and the use of context repositories are all achieved through specific subagents and skills. It utilizes three main skills:

* Memory initialization: Bootstraps new agents by exploring the codebase and reviewing historical conversation data (from Claude Code/Codex) using concurrent subagents that work in git worktrees to create the initial hierarchical memory structure.
* ‍Memory reflection:  A background "sleep-time" process that periodically reviews recent conversation history and persists important information into the memory repository with informative commit messages. It works in a git worktree to avoid conflicts with the running agent and merges back automatically.‍
* Memory defragmentation: Over long-horizon use, memories inevitably become less organized. The defragmentation skill backs up the agent's memory filesystem, then launches a subagent that reorganizes files, splitting large files, merging duplicates, and restructuring into a clean hierarchy of 15–25 focused files.

## Memory Across Sessions (Memory Persistence)
Rather than single infinite session, a more common workflow is operating a team of agents and subagents for some complex task. This this case, some sort of persistent memory is necessary so all these new agents can have a shared memory bank.

### [Claude-mem](https://github.com/thedotmack/claude-mem) (35,468 ★)

Popular tools to achieve this include [Claude-mem](https://github.com/thedotmack/claude-mem). It also functions as persistent memory for OpenClaw. Under the hood, it summarizes the session in a SQLite database, as well as a Chroma Vector DB for semantic lookup. During a new session, it uses a "Progressive Disclosure" strategy via its MCP search tools:
* Search (Layer 1): Claude uses the search tool to find relevant "indices" or IDs related to your current task (e.g., "Find where I worked on the login bug"). This costs very few tokens.
* Timeline (Layer 2): If the search is broad, it looks at the chronological context around those events to see what led up to them.
* Get_Observations (Layer 3): Only once Claude identifies a specific, relevant past action does it "fetch" the full, high-detail observation.

Claude-Mem stores chronological memory, and is a good tool for general session-to-session persistence. 

### [A-MEM](https://github.com/agiresearch/A-MEM) (886 ★)

Rather than just logging chronological history, [A-MEM](https://github.com/agiresearch/A-MEM?tab=readme-ov-file), based on the A-MEM [research paper](https://arxiv.org/pdf/2502.12110), is designed as a self-evolving knowledge graph. In A-MEM, every memory is a node.

When you add a memory via `add_memory_note`, it doesn't just save the text. It uses an LLM (like GPT-4o-mini or Claude) to:
1. Extract keywords, tags, and context.
2. Find "neighbor" memories using vector similarity.
3. Decide whether to link: It builds structural connections between the new memory and existing ones.
4. Evolve: It can strengthen existing links or update the tags of older memories based on the new information --> Newer memories impact past memories.

Like Claude-mem, it stores data and relationships in ChromaDB and metadata in SQLite.

During retrieval, the `search_memories_agentic` tool allows the agent to "follow the graph." It finds a relevant node and then explores connected notes, mimicking how a human might navigate their own thoughts. A-MEM appears to be better suited for building general knowledge of a complex codebase/architecture.

From the [authors](https://news.ycombinator.com/item?id=46636707):

> claude-mem uses a compaction approach. It records session activity, compresses it, and injects summaries into future sessions. Great for replaying what happened.
> 
> A-MEM builds a self-evolving knowledge graph. Memories aren’t compressed logs. They’re atomic insights that automatically link to related memories and update each other over time. Newer memories impact past memories.
> 
> For example: if Claude learns “auth uses JWT” in session 1, then learns “JWT tokens expire after 1 hour” in session 5, A-MEM links these memories and updates the context on both. The older memory now knows about expiration. With compaction, these stay as separate compressed logs that don’t talk to each other.

### [Graphiti](https://github.com/getzep/graphiti) (23,766 ★)

Graphiti focuses on *Temporal* Context Graphs. In Graphiti, every relationship has a validity window. If you tell the agent "I'm moving to Boston," Graphiti doesn't just overwrite your old city; it marks the old "lives in" relationship as "superseded" and creates a new one. It remembers what was true then versus what is true now.

While A-MEM uses an "Evolution" loop to keep its knowledge graph up-to-date, in Graphiti, a fact is "invalidated" by marking it with an end-timestamp (e.g., Fact A was true from Jan to March) to preserve temporal relationships with outdated memories.

Due to this history preservation feature, Graphiti is better suited for enterprises that requires audit logs and the understanding of past decision making.

### [Cognee](https://github.com/topoteretes/cognee) (13,843 ★)

Cognee also stores information in knowledge graphs, but allows the user to enforce an Ontology (a set of rules).

While A-MEM's knowledge graph is created free-form, the knowledge graph of Cognee is more structured, making it easier for AI to navigate around.

### [Engram](https://github.com/Harshitk-cp/engram) (15 ★)

Engram takes a cognitive science approach to Agentic memory.

It differs from the other solutions by attaching confidence to memories. Memories are assigned a confidence score (0.0-1.0), affecting how the agent loads them into context:
* Hot (>0.85): These are core beliefs. They are auto-injected into every prompt (e.g., "The user lives in NYC").
* Warm (0.70-0.85): Retrieved when the agent specifically searches for relevant context.
* Cold (0.40-0.70): Requires an explicit, high-effort query to find.
* Archive (<0.40): The memory is "forgotten" (soft-deleted).

Each new interaction with the user either reinforces a memory (increase confidence score) or contradicts with one (decrease confidence score). Just like a human brain, if a memory is never used or reinforced, it gradually loses confidence over time and eventually "fades" into the archive.

Memories are split into different databases by type:
* Semantic: General facts and preferences.
* Episodic: Specific past experiences and their outcomes.
* Procedural: Learned skills or "how-to" patterns.
* Working: Active session goals and immediate context.

Finally, Engram has an API for "Reflection." An agent can call `/cognitive/reflect` to look at its own memories and assess their quality or identify gaps in its own knowledge.

This is an even more nuanced approach than A-MEM, and may be even better suited for personal assistant usage scenarios.

## Local context
By "Local Context", I mean the context loaded by an Agent from local files during a new session. All the tools mentioned in the previous sections relies on databases for memory storage. Could it be easier/faster to store memory as local files instead?

Vector databases, used by the solutions mentioned above, face several challenges during memory retrieval, primarily stemming from their core design for semantic similarity rather than structured, stateful, or temporal information. They are retrieval systems, not true memory systems, which leads to issues like "embedding drift," difficulty with precise facts, and high operational overhead ([Redis Engineering Blog](https://redis.io/blog/common-challenges-working-with-vector-databases/)). Graph databases partially solves some of these issues, but they nonetheless remain.

### Strategically placed CLAUDE.md files
The most primitive way to store memory is to expand the local `AGENT.md` or `CLAUDE.md` files. However, as mentioned before, these files need to be kept lean. One strategy one can take is to break up repo instructions into directory-specific files

> CLAUDE.md files can live in several locations, each with a different scope. More specific locations take precedence over broader ones... CLAUDE.md files in [project] subdirectories load on demand when Claude reads files in those directories.
> 
> Claude Code reads CLAUDE.md files by walking up the directory tree from your current working directory, checking each directory along the way for CLAUDE.md and CLAUDE.local.md files. This means if you run Claude Code in foo/bar/, it loads instructions from both foo/bar/CLAUDE.md and foo/CLAUDE.md
>
> source: Anthropic [docs](https://code.claude.com/docs/en/memory)

What this means: Claude loads CLAUDE.md automatically when entering a directory. Because they load whether needed or not, their content must be minimal: a tabular index with short descriptions and triggers for when to open each file. Index may point to specific architectural details or histories and is loaded by the Agent only when needed.

By designing index files carefully, indices can act as a map of how documentations evolve -- thus mimicking knowledge graphs of graph databases.

### Local Indices

#### Claude Code
The source code of Claude Code was leaked at the end of March 2026. Examining the codebase, we see that it also prefers to use indexes to store memory ([AlphaSignal](https://alphasignal.ai/email/2f539f055e63c358)).

Claude Code loads a tiny index (MEMORY.md) into every prompt, where each line points to external files. When you ask something, the system fetches only the relevant file instead of dumping everything into the model. This avoids unnecessary token usage.

Another mechanism rewrites the memory as it "learns". A background process merges duplicates, removes contradictions, and deletes outdated facts. The system treats stale memory as incorrect and fixes it continuously.

Explore the python version of Claude Code [here (167k ★)](https://github.com/ultraworkers/claw-code?utm_source=alphasignal&utm_campaign=2026-04-01&lid=1q4s8wFRY84lryjvT).

#### Andrej Karpathy's personal knowledge base
Andrej Karpathy describes how he built a personal knowledge base by
1. Indexing all source documents into a `raw/` directory
2. Using an LLM to build a wiki -- a collection of markdown files
3. Asks LLM questions about his personalized wiki

{% include tweet.html url="https://twitter.com/karpathy/status/2039805659525644595" %}

He tweets about this workflow, done by using a collection of scripts, but the idea received thousands of positive responses.

To build your own knowledge base, first look at Andrej's detailed description of the idea [in more detail](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), and feed that into your own coding agent.

### [RepoAgent](https://github.com/OpenBMB/RepoAgent) (920 ★)

Not a true memory solution *per se*, but RepoAgent can be combined with pre-commit to perform automated code documentation. If you choose to stick with the Native implementation, RepoAgent is a lightweight tool to keep your documentation files up to date.

Modifying RepoAgent to update index files (e.g., with a custom Skill) can help achieve a greater cohesion across memory files.

### [OpenViking](https://github.com/volcengine/OpenViking) (12,105 ★)

Unlike all the other previous tools, OpenViking stores memory using a local filesystem, under `viking://`. Instead of just doing a "vague" semantic search, an agent can use commands like `ls` or the `Grep` tool and find to navigate specific "folders" (e.g., viking://user/memories/preferences/).

To save tokens, OpenViking automatically splits every piece of information into three layers:
* L0 (Abstract): A one-sentence summary for quick identification.
* L1 (Overview): A 2,000-token summary for general planning.
* L2 (Details): The full, raw data used only when deep reading is required.

This is akin to the directory-specific `CLAUDE.md` files mentioned previously.

One large advantage Viking provides is that it is not limited to text like vector DBs. It includes a multimodal engine designed to parse and understand images, audio, and video, creating unified semantic representations across all file types.

## Learning and Memory
An interesting idea is to "treat memory as a SKILL not a database" ([reddit](https://www.reddit.com/r/ClaudeAI/comments/1q7mp8m/what_is_the_best_tool_for_longrunning_agentic/nyhoz88/)). It is an active, cognitive process involving the dynamic selection, interpretation, and integration of information, not just passive storage and retrieval.

Looking across the solutions covered in this post, "learning" means very different things depending on the design philosophy:

| Solution | Learning Approach | How It Learns |
|----------|-------------------|---------------|
| **Memtree** | None (compression only) | Doesn't learn — restructures existing context into a B-tree for efficient retrieval, but doesn't update or evolve past memories |
| **Letta** | Active, scheduled reflection | A background "sleep-time" agent periodically reviews recent conversation history and writes structured updates back to the context repository; defragmentation reorganizes stale memories over time |
| **Claude-mem** | Passive compaction | Records session activity and compresses it into a SQLite/Chroma database; summaries are injected into future sessions but past entries are not updated |
| **A-MEM** | Evolving knowledge graph | When a new memory is added, an LLM links it to neighbor memories and can update the tags and context of _older_ memories — newer knowledge actively rewrites old knowledge |
| **Graphiti** | Temporal invalidation | Doesn't update old facts — it preserves them by marking them as "superseded" with an end-timestamp, maintaining a full audit trail of what was believed and when |
| **Cognee** | Structured graph growth | New facts are added as nodes within a predefined ontology; the structure is enforced rather than emergent, which makes navigation predictable but limits free-form evolution |
| **Engram** | Confidence-weighted reinforcement | Each interaction reinforces or weakens a memory's confidence score; memories that go unreinforced gradually fade to archive, closely mimicking biological forgetting and consolidation |
| **Native CLAUDE.md** | None (manual only) | Static files with no automated update mechanism; "learning" requires a human or agent to explicitly edit the files |
| **Claude Code (index-based)** | Active background rewriting | A background process merges duplicates, removes contradictions, and deletes outdated facts; the index is continuously kept correct rather than append-only |
| **Karpathy's wiki** | Manual LLM synthesis | Source documents are indexed into a `raw/` directory; an LLM generates a wiki from them on demand — learning happens at synthesis time, not incrementally |
| **RepoAgent** | Passive doc sync | Hooks into pre-commit to regenerate documentation from code changes; it tracks code drift, not agent knowledge |
| **OpenViking** | Layered progressive disclosure | Stores memories in L0/L1/L2 layers (abstract → full detail); learning is implicit in the act of writing new memory files, but there is no cross-memory evolution |

Among these, **A-MEM** and **Engram** are the most "learning-native" — they model how new information changes what the agent believes, not just what it has stored. **Letta's** sleep-time reflection is the most operationally complete: it actively synthesizes and persists insights without requiring manual curation.

### Active Learning as a Skill Pattern

Beyond dedicated memory systems, several projects implement learning as an explicit agent skill — a discrete, invocable action rather than an always-on background process. The "extract-learnings" skill in [Claudest](https://github.com/gupsammy/Claudest) is a focused example: after a session, the agent is explicitly prompted to identify what it learned, then writes that to a memory file. This is "learning on demand."

Other repos exploring this pattern:

* [Athena](https://github.com/winstonkoh87/Athena-Public) — a memory system that structures learnings around goals and tasks, letting the agent reflect on outcomes
* [ai-maestro](https://github.com/23blocks-OS/ai-maestro) — an orchestration framework that includes a learning loop for updating agent behavior based on feedback
* [context-hub-plugin](https://github.com/ScottRBK/context-hub-plugin), which runs [forgetful](https://github.com/ScottRBK/forgetful) under the hood — inspired by Andrew Ng's [Context Hub](https://github.com/andrewyng/context-hub), it includes a learning pattern for progressively building up API documentation and task-specific knowledge across sessions

## Honorable mentions
[AtlastMemory](https://github.com/Bpolat0/atlasmemory) -- only 5 ★ at the time of writing (4/4). 

## Further Reading

* [Memory - Anthropic](https://code.claude.com/docs/en/memory)
* [Effective Harnesses for Long-Running Agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
* [What is the best tool for long-running agentic tasks? - r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1q7mp8m/what_is_the_best_tool_for_longrunning_agentic/)
* [claude-config - solatis](https://github.com/solatis/claude-config)
* [What I learned building a memory system for my Claude agent - r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1r1w397/what_i_learned_building_a_memory_system_for_my/)
