---
layout: post
title: "Forget MCPs, Use CLI Tools Instead."
categories: [AI Coding, LLMs, Claude Code, Agentic AI, Developer Tools]
excerpt: "The MCP hype cycle is cresting. Influential developers and major companies are reverting to a simpler, older approach: the command-line interface."
---

When Anthropic released the Model Context Protocol in late 2024, the developer world declared it the "USB-C for AI" — a universal connector between language models and any tool or data source. Within months, thousands of MCP servers appeared on registries. Every SaaS company rushed to ship one. The ecosystem exploded.

Now the tide is turning. Influential developers are ripping out their MCP servers and going back to something they've relied on for decades: the humble CLI.

**TL;DR**
- MCP's core problem is token bloat: tool schemas consume enormous chunks of the context window before an agent sees a single user message
- Garry Tan (YC President), Denis Yarats (Perplexity CTO), and Peter Steinberger (OpenClaw Creator) have all publicly criticized MCP and moved away from it
- Thoughtworks (tech consultancy) placed "naive API-to-MCP conversion" in the **Hold** ring of their [Technology Radar](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf) (Nov 2025)
- LLMs are already deeply trained on CLI interactions — they can self-document with `--help` and need no schema
- CLI tools built as direct MCP replacements have emerged: `gstack`, `Playwright CLI`, and the existing `gh` (GitHub CLI)
- MCPs still have a place: SaaS products without CLIs, multi-tenant auth, and stateful workflows. If you must use MCPs, consider using tools that make them behave more like a CLI tool or an API call.

## Table of Contents <!-- omit from toc -->
- [The Promise](#the-promise)
- [The Backlash](#the-backlash)
- [Why MCPs Break in Practice](#why-mcps-break-in-practice)
  - [1. Token Bloat](#1-token-bloat)
  - [2. Auth Friction](#2-auth-friction)
  - [3. Reliability and Quality](#3-reliability-and-quality)
- [Why LLMs Are Already Good at CLIs](#why-llms-are-already-good-at-clis)
- [CLI Tools Built to Replace MCPs](#cli-tools-built-to-replace-mcps)
  - [gstack (★ 10,000+ in 48 hours)](#gstack--10000-in-48-hours)
  - [Playwright CLI (official Microsoft alternative)](#playwright-cli-official-microsoft-alternative)
  - [GitHub CLI (`gh`)](#github-cli-gh)
  - [Perplexity Agent API](#perplexity-agent-api)
  - [The Existing CLIs You Already Have](#the-existing-clis-you-already-have)
- [Where MCPs Still Win](#where-mcps-still-win)
  - [clihub — compile any MCP server into a CLI binary](#clihub--compile-any-mcp-server-into-a-cli-binary)
- [The Bottom Line](#the-bottom-line)
- [References](#references)
- [Further Reading](#further-reading)

## The Promise

MCP was designed to solve a real problem. Before MCP, connecting an AI agent to an external tool meant custom integration code for every combination. MCP proposed a standard: a JSON-RPC protocol over stdio or HTTP that any model could use to call any tool. Build one MCP server per tool, and every agent gets it for free.

The analogy to USB-C was apt. It promised interoperability. And in terms of adoption, it succeeded spectacularly — as of Q1 2026, there are over 17,000 MCP servers indexed across major registries, and OpenAI, Google, Microsoft, and AWS have all adopted the protocol [[1]].

But adoption and usefulness are not the same thing.

## The Backlash

The criticism has come from some of the most credible voices in the industry.

A post titled ["MCP is dead. Long live the CLI"][2] hit #1 on Hacker News on February 28, 2026 with ~300 comments [[3]]. The contributor, Eric Holmes, argued that LLMs are already expert at tools like `git`, `docker`, and `kubectl` — so why build a new abstraction on top of them? "I've lost count of the times I've restarted Claude Code because an MCP server didn't come up." CLI tools are just binaries. They're there when you need them and invisible when you don't.

**Peter Steinberger**, creater of OpenClaw, echoed this sentiment back in January:

{% include tweet.html url="https://twitter.com/steipete/status/2007876353463660757" %}

**Denis Yarats**, CTO and co-founder of Perplexity, announced at Ask 2026 (March 11, 2026) that Perplexity is moving away from MCP internally in favor of APIs and CLIs.His stated reason: MCP was consuming up to 72% of available context windows before an agent processed a single user message. Perplexity subsequently launched their Agent API — a single REST endpoint with built-in tools — as their preferred interface [[4]].

{% include tweet.html url="https://twitter.com/morganlinton/status/2031795683897077965" %}

Prominant industry voices echoed in concurrance. **Garry Tan**, President and CEO of Y Combinator, [put it bluntly on X][5] — and the frustration led directly to building gstack's browser CLI.

> "I got sick of Claude in Chrome via MCP and vibe coded a CLI wrapper for Playwright tonight in 30 minutes only for my team to tell me Vercel already did it lmao
>
> But it worked 100x better and was like 100LOC as a CLI"

**Paweł Huryn**, author of The Product Compass (the #3 product management newsletter on Substack with 106K+ subscribers), offered a more measured but equally pointed [take][6]: "His reasons are real: tool schemas eat context tokens, auth is clunky, and most MCP features go unused anyway."

**Thoughtworks** weighed in institutionally. The global software consultancy publishes a biannual [Technology Radar](https://www.thoughtworks.com/radar) — a report where their senior engineers document patterns and techniques observed across hundreds of client engagements. It's one of the more credible signals in the industry because it reflects real production experience rather than vendor marketing. Their Vol. 33 (November 2025) placed *"naive API-to-MCP conversion"* in the **Hold** ring — their designation for techniques teams should avoid [[7]]. "There has been a rush to convert APIs to MCP servers, which raises serious issues from both a security and efficiency perspective."

**Key takeaway**: This isn't just hobbyist frustration. The criticism is coming from YC's president, a major AI company's CTO, and a top engineering consultancy — all pointing to the same underlying problems.

## Why MCPs Break in Practice

The problems cluster around three root causes.

### 1. Token Bloat

Every MCP server dumps its entire tool schema into the context window at session start. The schemas include parameter types, descriptions, enum values, nested objects, and usage examples — all necessary for the model to know what a tool does, but enormously expensive in tokens.

Real-world measurements are stark:

| Task | CLI tokens | MCP tokens |
| ---- | ---------- | ---------- |
| Check repo language (`gh` vs GitHub MCP) | 1,365 [[8]] | 44,026 [[8]] |
| Browser automation (Playwright) | ~27,000 [[9]] | ~114,000 [[9]] |
| Session start* — GitHub MCP alone | — | ~55,000 (93 tool defs) [[10]] |
| Session start* — 3 servers (GitHub + Slack + Sentry) | — | 143,000 of 200,000 (72%) [[4]] |

*Session start = tokens consumed by tool schema definitions loaded before the user sends a single message.

> **Try it yourself**: Start a fresh Claude Code session and run `/context`. The "MCP tools" line shows exactly how many tokens your servers are consuming before you've said a word. Scott Spence measured his setup at 66,000 tokens consumed at conversation start — GitHub MCP alone accounting for 55,000 [[10]] [[11]].

This isn't a configuration problem — it's structural. MCP requires the schema to be transmitted at every session, regardless of how many tools the agent will actually use.

Cloudflare ran into this head-on. Their API has 2,500 endpoints — a native MCP implementation would consume ~244,000 tokens, exceeding most models' entire context window. Their solution, which they called "Code Mode" [[12]], keeps MCP for discovery but replaces tool-calling with code generation: the model writes code against a typed SDK and executes it directly. The result: 2,500 endpoints covered by 2 tools and ~1,000 tokens.

### 2. Auth Friction

MCP servers need to handle authentication. For a CLI tool, auth is already solved: you run `gh auth login` once, and the token lives in your OS credential store. For an MCP server, you need to implement an auth flow that works within the JSON-RPC protocol, often requiring custom solutions that are neither standard nor audited.

Holmes put it directly: "MCP is unnecessarily opinionated about auth. Why does a protocol for giving an LLM tools to use need to concern itself with authentication?"

### 3. Reliability and Quality

MCP servers are background processes. They can fail to start, hang, produce no output, or drop connections mid-session. The MCP registry has what one developer described as "the same quality problem as the npm registry circa 2016 — quantity does not imply reliability." [[13]]

Security researchers have found thousands of misconfigured MCP servers publicly accessible on the internet, with vulnerabilities including tool shadowing (one MCP server hijacking another's behavior) and prompt injection through tool output [[14]].

**Key takeaway**: MCP's token overhead is structural, not configurable. A three-server setup can consume 72% of your context window before you type a word.

## Why LLMs Are Already Good at CLIs

The CLI alternative works because of something MCP cannot replicate: training data.

Modern LLMs have been trained on billions of lines of terminal interactions, shell scripts, and documentation pages. When you ask Claude to use `git`, `docker`, `az`, `kubectl`, or `gh`, you're activating deeply learned patterns — not sending a schema it needs to parse.

**Self-documentation**: Give a coding agent shell access and point it at a CLI it's never seen before. It runs `--help`, reads the output, and starts using the tool correctly. No schema required. MCP has no equivalent mechanism.

**No overhead**: A CLI invocation adds zero tokens to the context window before the agent acts. The tool schema overhead that makes MCP expensive simply doesn't exist.

**No daemon**: CLI tools are stateless binaries. There's nothing to start up, nothing to keep alive, and nothing to restart when it hangs.

**Key takeaway**: LLMs don't need MCP to use tools effectively. For tools with good CLIs, the CLI is already the best interface.

## CLI Tools Built to Replace MCPs

The movement has produced concrete alternatives.

### gstack (★ 10,000+ in 48 hours)

Garry Tan's `gstack` [[15]] is a set of specialized workflows and skills that roleplays a team of opinionated YC advisors. `gstack` surpassed 10,000 GitHub stars in its first 48 hours after open-source release.

An often overlooked aspect of this repository is its browser CLI — a compiled Bun binary that talks to a persistent local Chromium daemon over HTTP. You get a real browser with real clicks and real screenshots at ~100ms per command, invoked like any other shell tool. No MCP server, no JSON schema, no background process to babysit — the daemon manages itself and shuts down after 30 minutes of idle time.

This is a direct answer to the Playwright MCP problem: instead of streaming entire accessibility trees into the model's context window, the CLI prints only what the agent asked for to stdout. Plain text, token-efficient, debuggable with `echo`.

### Playwright CLI (official Microsoft alternative)

Microsoft launched `Playwright CLI` in early 2026 as an explicit companion to — and replacement for — the Playwright MCP server [[9]]. Rather than streaming accessibility trees and screenshot bytes into the model's context (as MCP does), Playwright CLI saves everything to disk and lets the agent read only what it needs.

The result: 4× token reduction. A typical browser automation session costs ~27,000 tokens with the CLI versus ~114,000 with MCP. Some users report 10× gaps on longer sessions.

### GitHub CLI (`gh`)

The `gh` CLI already does everything the GitHub MCP server does — and agents already know how to use it. Community consensus has converged: "prefer using `gh` over this MCP," as one developer forum put it [[16]]. A comparison of the same task shows MCP using 32× more tokens than `gh` for identical results.

### Perplexity Agent API

Perplexity replaced their MCP-based tooling with a single REST endpoint that routes to models from OpenAI, Anthropic, Google, xAI, and NVIDIA with built-in tools like web search. One API key, OpenAI-compatible syntax, no schema overhead [[4]].

### The Existing CLIs You Already Have

For the major cloud and DevOps tools, MCP servers have been built — but they mostly reimplement what the official CLI already does. The agents already know how to use these tools natively. One real-world comparison found a 35× token reduction when switching from MCP to CLI for identical tasks [[17]]:

| Tool | MCP server exists? | Better approach |
| ---- | ------------------ | --------------- |
| GitHub | Yes (official) | `gh` CLI — agents know it deeply, 32× fewer tokens |
| AWS | Yes (AWS Labs) | `aws` CLI — already in training data |
| Kubernetes | Yes | `kubectl` — battle-tested, zero schema overhead |
| Docker | Yes | `docker` CLI — universally understood |
| Terraform | Yes (HashiCorp) | `terraform` CLI — though MCP adds live registry docs |

The pattern: if the vendor shipped a CLI before they shipped an MCP server, default to the CLI.

**Key takeaway**: The alternatives aren't theoretical — they're shipping and gaining traction fast. And in many cases, you already have them installed.

## Where MCPs Still Win

This isn't an argument to abandon MCP entirely. There are cases where it remains the right tool:

- **SaaS products without a CLI** — there's simply no CLI to use
- **Multi-tenant auth (OAuth per user)** — MCP handles per-user auth flows better than CLI credential stores
- **Stateful, long-running sessions** — MCP maintains connection state across interactions
- **Sandboxed environments** — when the agent has no shell access, MCP is the only option

What I'm cautioning against is treating it as the *default* answer for every AI integration, which the industry did in 2025. As Thoughtworks put it: the antipattern is *naive API-to-MCP conversion*, not MCP itself.

### [clihub][18] — compile any MCP server into a CLI binary
If you must use an MCP, consider adopting [`clihub`][18]. It compiles an MCP server into a standalone CLI binary. Every tool the server exposes becomes a subcommand with flags derived from its JSON Schema. Auth is handled automatically. The generated binary has no runtime dependencies — no config files, no clihub needed at runtime.

This matters for the "SaaS without a CLI" problem. If you're stuck with an MCP server you can't replace, clihub gives you the token efficiency of a CLI without rewriting anything.

## The Bottom Line

MCP solved a real problem and succeeded at achieving adoption. But the ecosystem over-indexed on it, and the costs are now visible: context windows consumed before a single message, auth friction that adds no security value, background processes that crash, and servers of wildly varying quality.

For tools with solid CLIs — GitHub, Docker, cloud providers, databases — the CLI is already the better interface. LLMs know how to use it, it's zero overhead, and it doesn't require a persistent server.

The pattern emerging from `gstack`, Playwright CLI, and the broader developer community points in one direction: treat MCP as a specialized tool for specific cases, not a default layer for all AI integrations. Reach for the CLI first.

## References

[1]: https://workos.com/blog/2026-mcp-roadmap-enterprise-readiness "MCP's 2026 Roadmap Makes Enterprise Readiness a Top Priority — WorkOS"
[2]: https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html "MCP is dead. Long live the CLI — Eric Holmes"
[3]: https://news.ycombinator.com/item?id=47380270 "MCP is dead; long live MCP — Hacker News"
[4]: https://awesomeagents.ai/news/perplexity-agent-api-mcp-shift/ "Perplexity CTO Moves Away from MCP Toward APIs and CLIs — Awesome Agents"
[5]: https://x.com/garrytan/status/2031910564344262988 "Garry Tan on MCP — X"
[6]: https://x.com/PawelHuryn/status/2032360024589164929 "Paweł Huryn on Perplexity's MCP move — X"
[7]: https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf "Technology Radar Vol. 33 — Thoughtworks"
[8]: https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/ "MCP vs CLI: Benchmarking Tools for Coding Agents — Mario Zechner"
[9]: https://scrolltest.medium.com/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0 "Playwright MCP Burns 114K Tokens Per Test. The New CLI Uses 27K. — ScrollTest"
[10]: https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code "Optimising MCP Server Context Usage in Claude Code — Scott Spence"
[11]: https://www.jdhodges.com/blog/claude-code-context-slash-command-token-usage/ "Claude Code /context Command: See Where Your Tokens Go — JD Hodges"
[12]: https://blog.cloudflare.com/code-mode-mcp/ "Code Mode: give agents an entire API in 1,000 tokens — Cloudflare"
[13]: https://dev.to/neopotato/the-mcp-server-crisis-how-open-standard-created-a-wild-west-of-broken-implementations-115n "The MCP Server Crisis: How 'Open Standard' Created a Wild West of Broken Implementations — DEV Community"
[14]: https://repello.ai/blog/mcp-vs-cli "MCP vs CLI: What Perplexity's Move Actually Means for AI Security Teams — Repello AI"
[15]: https://github.com/garrytan/gstack "gstack — GitHub"
[16]: https://smartscope.blog/en/Tips/GitHub/github-gh-mcp-comparison-guide/ "GitHub Operations in the AI Coding Era: gh vs MCP — SmartScope"
[17]: https://www.scalekit.com/blog/mcp-vs-cli-use "MCP vs CLI: Benchmarking AI Agent Cost & Reliability — Scalekit"
[18]: https://github.com/thellimist/clihub "clihub — Turn any MCP server into a CLI binary — GitHub"

1. [MCP's 2026 Roadmap — WorkOS](https://workos.com/blog/2026-mcp-roadmap-enterprise-readiness)
2. [MCP is dead. Long live the CLI — Eric Holmes](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html)
3. [MCP is dead; long live MCP — Hacker News](https://news.ycombinator.com/item?id=47380270)
4. [Perplexity CTO Moves Away from MCP — Awesome Agents](https://awesomeagents.ai/news/perplexity-agent-api-mcp-shift/)
5. [Garry Tan on MCP — X](https://x.com/garrytan/status/2031910564344262988)
6. [Paweł Huryn on Perplexity's MCP move — X](https://x.com/PawelHuryn/status/2032360024589164929)
7. [Technology Radar Vol. 33 — Thoughtworks](https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf)
8. [MCP vs CLI: Benchmarking — Mario Zechner](https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/)
9. [Playwright MCP Burns 114K Tokens — ScrollTest](https://scrolltest.medium.com/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0)
10. [Optimising MCP Server Context Usage — Scott Spence](https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code)
11. [Claude Code /context Command: See Where Your Tokens Go — JD Hodges](https://www.jdhodges.com/blog/claude-code-context-slash-command-token-usage/)
12. [Code Mode: give agents an entire API in 1,000 tokens — Cloudflare](https://blog.cloudflare.com/code-mode-mcp/)
13. [The MCP Server Crisis — DEV Community](https://dev.to/neopotato/the-mcp-server-crisis-how-open-standard-created-a-wild-west-of-broken-implementations-115n)
14. [MCP vs CLI: What Perplexity's Move Means — Repello AI](https://repello.ai/blog/mcp-vs-cli)
15. [gstack — GitHub](https://github.com/garrytan/gstack)
16. [gh vs MCP Comparison — SmartScope](https://smartscope.blog/en/Tips/GitHub/github-gh-mcp-comparison-guide/)
17. [MCP vs CLI: Benchmarking AI Agent Cost & Reliability — Scalekit](https://www.scalekit.com/blog/mcp-vs-cli-use)
18. [clihub — Turn any MCP server into a CLI binary — GitHub](https://github.com/thellimist/clihub)

## Further Reading

- [MCP is dead. Long live the CLI — Eric Holmes](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html)
- [MCP is dead; long live MCP — Hacker News discussion](https://news.ycombinator.com/item?id=47380270)
- [Everything wrong with MCP — Hacker News](https://news.ycombinator.com/item?id=43676771)
- [Your MCP Server Is Eating Your Context Window — APIdeck](https://www.apideck.com/blog/mcp-server-eating-context-window-cli-alternative)
- [Why CLI Tools Are Beating MCP for AI Agents — Janni Kreinhard](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/)
- [MCP vs. CLI for AI agents: How to choose — Manveer C.](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents)
- [Replace MCP With CLI — Cobus Greyling](https://cobusgreyling.substack.com/p/replace-mcp-with-cli-the-best-ai)
