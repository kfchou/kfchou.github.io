---
layout: post
title: "Beyond Plan & Build: Workflow Repos That Enforce Engineering Discipline"
categories: [AI Coding, LLMs]
excerpt: "The current most popular open-source repositories that prescribe and enforce end-to-end development workflows for AI coding assistants: Superpowers, gstack, and OpenSpec/Spec-Kit."
---

TL;DR - Only concerned with building specific features? Use [superpowers](#tdd-enforcement) to help enforce test-driven development. Building for production? Best plan and review with [gstack](#enforcing-the-entire-sprint-process). Working in a large org with interdisciplinary stakeholders? Best write some specs with [OpenSpec](#sdd-enforcement) or [spec-kit](#sdd-enforcement).

| Repo | Scope | Philosophy |
|---|---|---|
| [obra/superpowers][1] (115k ★) | Individual — feature discipline | Agents fail from process failures, not capability gaps |
| [garrytan/gstack][2] (49k ★) | Team — sprint rigor and shipping | Completeness is now cheap — always do the complete thing |
| [github/spec-kit][8] (82.7k ★) + [OpenSpec][9] (34.6k ★) | Cross-team — what to build | Specs become executable; implementation flows from them |


The thing that separates skilled AI developers from vibecoders isn't just better prompts -- it's having a process. Skilled engineers and teams consistently producing high-quality work by following good processes. When those processes and procedures are codified into something an AI can follow, it helps developers achieve high-quality results in a fraction of the time.

A basic example of this is the plan -> build workflow in coding harnesses like Claude and Cursor. This may be sufficient for small scopes of work. But when working in a large project, a robust process is needed beyond those two steps. A distinct category of repository has emerged recently to capture workflows of good engineering practices. On the surface, they're another skill/prompt collection. Take a closer took, and you'll find these collections of skills and prompts prescribe and enforce end-to-end development workflows for AI coding assistants, making them work like actual engineers.

Here, I cover three different approaches, or workflows, that you should consider when building with AI. Each embodies a different philosophy and cover a different part of the development lifecycle. Each draws on established software engineering practice (TDD, sprint discipline, spec-first design). They differ in scope. They target distinct failure modes of AI development. They may somewhat overlap, but they are also complementary. Understanding them, and incorporating these into your workflow can be the difference between churning out AI slop versus production-quality engineering work.


## Table of Contents <!-- omit from toc -->

- [Process Discipline Inside a Feature](#process-discipline-inside-a-feature)
  - [TDD Enforcement](#tdd-enforcement)
- [Sprint Rigor and the Economics of Completeness](#sprint-rigor-and-the-economics-of-completeness)
  - [Enforcing the entire sprint process](#enforcing-the-entire-sprint-process)
- [Spec-Driven Development: The Spec as the Source of Truth](#spec-driven-development-the-spec-as-the-source-of-truth)
  - [SDD Enforcement](#sdd-enforcement)
- [How They Relate](#how-they-relate)
- [Honorable Mention: shinpr/claude-code-workflows](#honorable-mention-shinprclaude-code-workflows)
- [Now What?](#now-what)
- [References](#references)
- [Further Reading](#further-reading)

## Process Discipline Inside a Feature

The engineering practice here is **Test-Driven Development (TDD)** and a broader cluster of process gates that experienced teams enforce before, during, and after implementation.

TDD follows a strict cycle: write a failing test first (RED), write the minimum code to pass it (GREEN), then refactor for quality without breaking the test (REFACTOR). The discipline is the *order* — you cannot skip the failing test, because that's the moment you define what "correct" means before you write any implementation. Code written test-first tends to be more modular, more focused, and easier to debug, because the test forces you to think about the interface before the internals.

Beyond TDD, experienced engineers follow a constellation of process gates when building a feature: brainstorm and plan before touching code, implement in an isolated branch so work doesn't pollute the main codebase, review the implementation against the original plan before merging, and verify the full test suite passes before declaring work complete. Each gate exists because skipping it creates a specific, well-documented class of problem — implementation that drifts from the design, tests retrofitted after the fact that test behavior rather than intent, "done" features that break on edge cases no one thought to check.

**Why and how they're used**: In large teams, these gates are enforced by culture and tooling together — PR templates require a test plan section, CI blocks merges below coverage thresholds, code review checklists exist precisely to catch what the author misses. Junior engineers learn this process through peer review friction. The cost of skipping a gate is made visible to others.

**When it's useful**: Most valuable when work spans multiple files, when any non-trivial logic is involved, and whenever the difference between "working" and "correct" depends on a verification step that's easy to skip under time pressure.

**Issues for AI agents**: The challenge with AI coding assistants isn't that they don't know these practices — it's that they rationalize around them. Under time pressure, an agent starts debugging immediately instead of following the debugging protocol. When code works, it commits rather than checking whether the implementation meets the established pattern. The process collapses exactly when discipline is most needed.

### TDD Enforcement

Jesse Vincent (known for his work with the Perl programming language) built [superpowers](https://github.com/obra/superpowers) to address this directly. The solution it takes is unusual: it embeds persuasion principles directly into skill instructions to make compliance more reliable. Vincent found that Robert Cialdini's influence principles — authority, commitment, scarcity, social proof — work on LLMs the same way they work on humans [[4]].

The framework validates this with pressure-testing. Before a skill is considered production-ready, it runs against realistic scenarios: a production system down at $5k/minute — do you read the debugging skill first or start debugging immediately? Forty-five minutes into working code — do you check the testing skill before committing? The skill fails if the agent takes the shortcut.

It enforces the following stages across a feature:

| Stage | Skill | What it does |
|---|---|---|
| 1 | brainstorming | Talks through the plan before touching code |
| 2 | using-git-worktrees | Creates an isolated branch and clean test baseline |
| 3 | writing-plans | Breaks work into tasks with exact file paths and verification steps |
| 4 | subagent-driven-development | Dispatches subagents per task; reviews each before continuing |
| 5 | test-driven-development | Enforces RED → GREEN → REFACTOR; failing test before implementation |
| 6 | requesting-code-review | Reviews against the plan; critical issues block progress |
| 7 | finishing-a-development-branch | Verifies tests pass; presents merge/PR/discard options |

*"I can't recommend this post strongly enough. The way Jesse is using these tools is wildly more ambitious than most other people."* - Simon Willison (co-creator of Django, creator of Datasette) [[5]]

**Key takeaway**: superpowers is most valuable when you're operating within a feature context — designing, implementing, writing tests. The workflow enforces planning before code, tests before implementation, and verification before declaring done.

> **Try it yourself**: Install via `/plugin marketplace add obra/superpowers-marketplace`, then start a feature with `brainstorm` and follow where the workflow takes you.

## Sprint Rigor and the Economics of Completeness

The engineering practice here is **Agile sprint discipline** — the structured cadence by which well-run teams move from idea to shipped code.

In a typical sprint workflow: ideas are scoped and architecturally reviewed before implementation begins, code review catches logic errors and design drift before merge, QA verifies user-facing behavior against acceptance criteria in conditions that resemble production, and retrospectives surface what the team learned so the process improves. Each step is a gate, and each gate has a specific failure mode it exists to prevent.

**Code review** is more than a style check. In strong engineering cultures, reviewers look for security boundary violations, race conditions, and edge cases that unit tests don't catch — the class of bugs that pass CI but cause production incidents. **QA** is distinct from automated testing: it verifies actual user-facing behavior with a real browser and real data flows, not a test harness that mocks the hard parts away. **Retrospectives** are how the team improves its *process*, not just its code — reviewing what slipped through, what took longer than expected, and what would change the next sprint.

**Why and how they're used**: Sprint ceremonies reduce the cost of mistakes by catching them at the right stage. A bug found in code review costs minutes. The same bug found in production costs hours or days, plus customer impact. The ceremonies also create shared understanding — architecture reviews surface disagreements before implementation locks them in; retrospectives distribute knowledge that would otherwise stay siloed.

**When it's useful**: Most relevant when moving from idea through architecture, implementation, review, QA, and ship as a complete cycle. More valuable the higher the stakes: production systems, public-facing features, teams with more than one developer touching the same codebase.

**What shifts with AI**: The cost of doing sprint-level work *completely* has dropped dramatically. Test suites, edge case coverage, full implementation over a partial one — these used to involve genuine time tradeoffs. With AI, that margin has narrowed considerably. This changes which shortcuts are still justified.

### Enforcing the entire sprint process

Garry Tan (CEO of Y Combinator) released gstack in March 2026 built around this argument. The ETHOS.md states it directly with a compression ratio table [[6]]:

| Task type | Human team | AI-assisted | Compression |
|---|---|---|---|
| Boilerplate / scaffolding | 2 days | 15 min | ~100x |
| Test writing | 1 day | 15 min | ~50x |
| Feature implementation | 1 week | 30 min | ~30x |
| Bug fix + regression test | 4 hours | 15 min | ~20x |
| Architecture / design | 2 days | 4 hours | ~5x |

gstack calls this "boil the lake" — *"The last 10% of completeness that teams used to skip? It costs seconds now."* Always do the complete thing when the lake is boilable.

The workflow gstack prescribes runs from idea to shipped:

| Stage | Skill | What it does |
|---|---|---|
| 1 | office-hours | Six forcing questions that reframe the product before you write code |
| 2 | plan-ceo-review / plan-eng-review | Lock architecture, test strategy, design specs |
| 3 | Build | Implementation, with design decisions flowing downstream |
| 4 | review | Find bugs that pass CI but blow up in production |
| 5 | qa | Browser-based QA with real Chromium; atomic commits |
| 6 | ship | Sync main, run tests, audit coverage, push, open PR |
| 7 | retro | Weekly retrospective against commit history |

Each stage produces artifacts the next one consumes: `/plan-eng-review` writes a test plan that `/qa` picks up; bugs flagged by `/review` must be resolved before `/ship` proceeds. The README is explicit: *"Nothing falls through the cracks because every step knows what came before it."*

The standout is the review process. `/review` isn't a linter wrapper — it runs structured analysis for SQL injection, LLM trust boundary violations, and conditional side effects: failure modes that pass automated checks but cause production incidents. `/qa` opens a real browser, not a headless test runner, and verifies actual user-facing behavior.

**Key takeaway**: gstack is most valuable at the sprint level — from idea through ship. The review and QA stages in particular catch the class of bugs that automated tests miss.

> **Try it yourself**: Install via `/plugin marketplace add garrytan/gstack-marketplace`, then try `/review` on your next PR before merging.

## Spec-Driven Development: The Spec as the Source of Truth

Spec-first design has a long history in software engineering — requirements engineering, BDD, ATDD — and it's worth understanding where those practices come from, because the AI tools are solving the same underlying problem they were invented to solve.

**The problem** in any team larger than a few people: requirements live in someone's head. Developers implement based on their interpretation, QA tests against theirs, and the PM reviews against the original intent. By the time you discover the mismatch, you've built the wrong thing. The later you catch it, the more expensive it is to fix.

**BDD (Behavior-Driven Development)** is a response to this. It formalizes requirements as observable, executable behaviors written in a structured natural language called Gherkin:

```gherkin
Feature: User login
  Scenario: Valid credentials
    Given a registered user with email "alice@example.com"
    When they submit correct credentials
    Then they see their dashboard
    And a session token is issued
```

The key property: this is readable by non-engineers *and* executable by test frameworks like Cucumber or Pytest-BDD. The product manager who wrote the acceptance criteria can read the test. When the test fails, everyone agrees on what broke — there's no argument about what "done" means.

**ATDD (Acceptance Test-Driven Development)** is the broader process that produces those specs. The sequence: write acceptance tests *before* any implementation begins, then develop until they pass. In practice, teams formalize this with a **Three Amigos** meeting — product manager, developer, and QA — held before sprint work starts. The PM brings *what* to build, the developer raises *how*, and QA surfaces *what could go wrong*. The output is acceptance criteria written as executable tests, committed to the repository. Passing tests are the objective definition of done.

In large teams, this compounds in value over time. Acceptance tests accumulate into a regression suite that catches behavioral drift across sprints. New engineers can read the spec directory to understand intent, not just implementation. Cross-team contracts — "our service will do X when you call it with Y" — become verifiable rather than informal. The shared artifact prevents the slow drift where everyone has a slightly different understanding of what the system is supposed to do.

**What the AI context adds** is a failure mode BDD and ATDD alone don't address. Human engineers at least share context — they've read the same ticket, attended the same planning meeting, and can ask questions. AI coding assistants resolve ambiguity silently, toward whatever is most straightforward. Without an explicit spec, that means filling in blanks with plausible-looking code that satisfies the letter of the request but misses the intent. The spec needs to remain the contract throughout — not just as initial input, but as the artifact tests are held against and as a record that persists after the feature ships.

**When it's useful**: Most relevant when requirements are still fuzzy, when you're working in a codebase large enough that mid-implementation pivots are expensive, or when you're building cross-team features where multiple people need to agree on exactly what the system will do.

### SDD Enforcement

Two repos independently arrived at a spec-driven approach in August 2025 and now represent distinct implementations — each mapping directly onto the ATDD workflow, with the spec as the artifact that persists through and after implementation.

[github/spec-kit][8] (82.7k stars), from GitHub Next, takes a structured approach. The workflow is five sequential stages:

| Stage | Command | What it does |
|---|---|---|
| 1 | `/speckit.constitution` | Establishes project principles, coding standards, and quality bars |
| 2 | `/speckit.specify` | Describes *what* to build — product scenarios, not tech stack |
| 3 | `/speckit.plan` | Adds architectural and technical implementation choices |
| 4 | `/speckit.tasks` | Breaks the plan into a concrete, ordered task list |
| 5 | `/speckit.implement` | Executes all tasks against the spec |

[OpenSpec][9] (34.6k stars) predates spec-kit by two weeks and takes a different stance: "fluid not rigid, iterative not waterfall." Its key differentiator is that specs are persistent files on disk — each feature generates a `openspec/changes/<feature>/` directory with `proposal.md`, `specs/`, `design.md`, and `tasks.md`. After implementation, `/opsx:archive` moves those files to a timestamped archive. Your project accumulates a history of *why* things were built, not just what was built. It's also explicitly designed for brownfield projects, not just greenfield.

```text
You: /opsx:propose add-dark-mode
AI:  Created openspec/changes/add-dark-mode/
     ✓ proposal.md, specs/, design.md, tasks.md

You: /opsx:apply
AI:  All tasks complete.

You: /opsx:archive
AI:  Archived to openspec/changes/archive/2026-03-26-add-dark-mode/
```

The tradeoff: spec-kit's structured stages are better for greenfield work where you want strong guardrails from the start. OpenSpec's fluid model is better when requirements are still evolving or you're adding to an existing codebase.

Both build on the same foundation as superpowers and gstack: superpowers asks *how do we execute with discipline?* gstack asks *are we shipping it completely?* SDD tools ask *are we building the right thing in the first place?* The spec becomes the contract that both the implementation and the tests are held against — making all three complementary.

**Key takeaway**: Reach for an SDD tool when the requirement is still fuzzy. spec-kit if you want structured stages; OpenSpec if you need flexibility or are working brownfield.

> **Try it yourself**: spec-kit — `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`, then `specify init . --ai claude`. OpenSpec — `npm install -g @fission-ai/openspec && openspec init`, then `/opsx:propose <your idea>`.

## How They Relate

Where these overlap, they're additive rather than redundant. superpowers enforces discipline during implementation; gstack enforces completeness at the sprint level; SDD tools ensure you're building the right thing before any of that begins. The SDD spec becomes the contract superpowers' tests are written against. superpowers' `requesting-code-review` and gstack's `/review` operate at different granularities — one checks implementation against the plan, the other checks for production failure modes that pass automated testing. They can be used independently or layered depending on how much of the process needs more structure.

## Honorable Mention: shinpr/claude-code-workflows

With 248 stars, [shinpr/claude-code-workflows][3] is smaller than the others but takes the same approach: end-to-end workflow over tool collection. Its pipeline runs requirement-analyzer → design doc (PRD for large features, tech spec for medium) → implementation → QA. A separate `metronome` add-on detects when Claude is taking shortcuts mid-workflow and nudges it back on track.

Worth watching, especially for teams that want an explicit separation between requirements, design, and implementation as distinct workflow stages.

## Now What?

Pick a philosophy, install it, and run one real feature through it. The workflows above are most valuable when you follow them end-to-end at least once — the structure only reveals itself in practice.

Once you have a workflow in place, there's a separate class of tooling worth knowing about: infrastructure that runs *for* you rather than *with* you. [GitHub Agentic Workflows][7] (currently in technical preview) is the clearest example — you describe the outcome you want in a Markdown file, and agents handle it on a schedule or repository trigger via GitHub Actions. Issue triage, documentation sync, test coverage improvement, CI failure investigation — the maintenance work that falls through the cracks not because no one cares, but because no one has time. The workflows in this post cover how you build; GitHub Agentic Workflows covers what keeps a repository healthy between sprints.

## References

[1]: https://github.com/obra/superpowers "obra/superpowers — GitHub"
[2]: https://github.com/garrytan/gstack "garrytan/gstack — GitHub"
[3]: https://github.com/shinpr/claude-code-workflows "shinpr/claude-code-workflows — GitHub"
[4]: https://blog.fsck.com/2025/10/09/superpowers/ "Superpowers: How I'm using coding agents in October 2025 — Jesse Vincent"
[5]: https://news.ycombinator.com/item?id=45547344 "HN: Superpowers — 435 points, 231 comments"
[6]: https://github.com/garrytan/gstack/blob/main/ETHOS.md "gstack ETHOS.md"
[7]: https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/ "Automate repository tasks with GitHub Agentic Workflows"
[8]: https://github.com/github/spec-kit "github/spec-kit — GitHub"
[9]: https://github.com/Fission-AI/OpenSpec "Fission-AI/OpenSpec — GitHub"

1. [obra/superpowers — GitHub](https://github.com/obra/superpowers)
2. [garrytan/gstack — GitHub](https://github.com/garrytan/gstack)
3. [shinpr/claude-code-workflows — GitHub](https://github.com/shinpr/claude-code-workflows)
4. [Superpowers: How I'm using coding agents in October 2025 — Jesse Vincent](https://blog.fsck.com/2025/10/09/superpowers/)
5. [HN: Superpowers — 435 points, 231 comments](https://news.ycombinator.com/item?id=45547344)
6. [gstack ETHOS.md](https://github.com/garrytan/gstack/blob/main/ETHOS.md)
7. [Automate repository tasks with GitHub Agentic Workflows](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)
8. [github/spec-kit — GitHub](https://github.com/github/spec-kit)
9. [Fission-AI/OpenSpec — GitHub](https://github.com/Fission-AI/OpenSpec)

## Further Reading

- [github/spec-kit](https://github.com/github/spec-kit) — the repo, with workflow gallery and community extensions
- [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) — the fluid, brownfield-friendly alternative
- [Agentic Code Development with Claude Code]({% post_url 2026-01-07-agentic-coding %}) — this blog's primer on skills vs subagents
- [Superpowers: How I'm using coding agents in October 2025](https://blog.fsck.com/2025/10/09/superpowers/) — Jesse Vincent's original post
- [Simon Willison's notes on superpowers](https://simonwillison.net/2025/Oct/10/superpowers/)
- [gstack ETHOS.md](https://github.com/garrytan/gstack/blob/main/ETHOS.md) — the full philosophy behind gstack
