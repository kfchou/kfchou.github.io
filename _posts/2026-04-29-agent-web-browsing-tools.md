---
layout: post
title: "Web Browsing Tools for CLI Agents: Three Tiers on the Capability Axis"
categories: [AI Coding, LLMs, Agents, Web Browsing]
excerpt: "From WebFetch to Computer Use — the landscape of web tools available to CLI agents, the tradeoffs across speed, safety, and site coverage, and recommended combinations for common use cases."
---

TL;DR — What tools are available for Agnetic web browsing? I map web tools for Agents along a single axis from "cheap, safe, limited" to "expensive, risky, capable". They can be roughly categorized into three tiers: **read-only fetch**, **deterministic browser**, and **AI-driven action**. Each tier has a default tool, and most production agents combine 2–3 across tiers depending on the task. Stick with the lowest tier necessary — every step up costs ~10–100x more and widens the prompt-injection blast radius. Depending on your use case, I recommend five combinations of tools to employ.

## Table of Contents <!-- omit from toc -->

- [The capability axis](#the-capability-axis)
- [Quick primer: the browser automation stack](#quick-primer-the-browser-automation-stack)
- [Tier 1: Read-only fetch](#tier-1-read-only-fetch)
- [Tier 2: Deterministic browser](#tier-2-deterministic-browser)
- [Tier 3: AI-driven action](#tier-3-ai-driven-action)
- [Cross-cutting: anti-bot infrastructure](#cross-cutting-anti-bot-infrastructure)
- [Safety: the prompt-injection problem](#safety-the-prompt-injection-problem)
- [The "best combination" matrix](#the-best-combination-matrix)
  - [Combination A — Research / RAG agent](#combination-a--research--rag-agent)
  - [Combination B — Coding / dev agent](#combination-b--coding--dev-agent)
  - [Combination C — Web QA / regression pipeline](#combination-c--web-qa--regression-pipeline)
  - [Combination D — Open-ended operator agent](#combination-d--open-ended-operator-agent)
  - [Combination E — High-volume scrape / RAG ingestion](#combination-e--high-volume-scrape--rag-ingestion)
- [Common pitfalls](#common-pitfalls)
- [References](#references)

## The capability axis

![Three tiers on the capability axis: read-only fetch, deterministic browser, AI-driven action — with anti-bot infrastructure as an optional wrapper](/assets/2026-04-29-agent-web-browsing-tools/browsing-tool-tiers.png)

Three tiers along the axis:

1. **Cost grows ~10–100x per tier.** A WebSearch call is a few cents; a Playwright MCP click is sub-second and free of LLM inference; a Browser Use task can run \$0.30 [[1]].
2. **Blast radius grows with capability.** Tier 1 fetches text into context. Tier 2 can click and submit forms but only the actions you script. Tier 3 hands the LLM the steering wheel — anything it reads can become an instruction it follows.
3. **Sites stratify by which tier can reach them.** A static news article (clean HTML, OpenGraph meta tags) is Tier 1. A JavaScript-heavy app where content only appears after the page boots — a React or Vue dashboard, a single-page app — is Tier 2. A site with login + 2FA + Cloudflare is Tier 3 plus anti-bot infrastructure.

The recommended combinations at the [bottom of the post](#the-best-combination-matrix) are concrete picks across these tiers for common agent shapes.

## Quick primer: the browser automation stack

When an agent drives a browser, several layers stack on top of each other. Knowing the stack makes the rest of the post easier to read:

1. **Browser engine** — **Chromium** is the open-source project Google maintains. Chrome, Edge, Brave, Arc, and Opera are all built on it. It's the code that parses HTML, runs JavaScript, and paints pixels. Almost every agent-browsing tool drives Chromium under the hood. Firefox uses Gecko and Safari uses WebKit; both can be driven too, but Chromium dominates.
2. **Wire protocol** — **Chrome DevTools Protocol (CDP)** or the older **W3C WebDriver** protocol. This is the JSON-RPC channel that an external process uses to tell the browser "click this element," "navigate to this URL," "return the DOM." It's how anything outside the browser controls what's inside.
3. **Automation library** — **Playwright** (Microsoft, modern, fast), **Puppeteer** (Google, predates Playwright), and **Selenium** (2004, WebDriver-based) wrap CDP/WebDriver in a language-level API. Selenium is the legacy QA standard; agents almost never use it directly because Playwright wins on speed, debug tooling, and auto-wait semantics [[2]].
4. **MCP server** — **Model Context Protocol** is Anthropic's open protocol for exposing tools to LLMs. An MCP server is a small process that wraps a library (e.g. Playwright) and advertises tools (`browser_click`, `browser_navigate`) over JSON-RPC; an MCP-aware client (Claude Code, Cursor, Copilot) auto-discovers and calls them. Most browser-automation tools ship an MCP server because it's the cheapest way to plug into popular agent harnesses.
5. **Agent harness** — Claude Code, Cursor, Copilot CLI, your custom agent. The LLM-driving program that connects to MCP servers and decides which tools to call.

So `Playwright MCP` is shorthand for the full stack: an **MCP server** (level 4) that wraps the **Playwright library** (level 3) which talks **CDP** (level 2) to **Chromium** (level 1), all driven by an **agent harness** (level 5). When the post says "the agent uses Playwright MCP," all five layers are involved.

## Tier 1: Read-only fetch

**The job:** turn a URL or query into clean text in the agent's context. No clicking, no auth, no JavaScript rendering (with one exception, noted below).

**The tools:**

| Tool | What it does | Cost | Notable |
| --- | --- | --- | --- |
| Anthropic `WebSearch` | Search → titles, URLs, encrypted snippets, citations | \$10 / 1,000 searches [[3]] | New `web_search_20260209` adds dynamic filtering — Claude writes code to post-process results before they hit context |
| Anthropic `WebFetch` | URL → markdown via small fast model + 15-min cache | Standard token costs | Fails on auth-walled URLs; redirect-flags and asks for re-fetch |
| [Jina Reader][4] (`r.jina.ai`) | Prepend `r.jina.ai/` to any URL → markdown | Free up to 20 RPM, 10M tokens free with key | ~2–8s latency; handles light JS; works as a curl replacement |
| [Crawl4AI][5] (64.8k ★) | Async crawler, BM25/heuristic content filtering, full Chromium when needed | Free, self-hosted | Straddles Tier 1 and Tier 2 — runs a real browser but exposes a markdown-out API |
| [Tavily MCP][6] (1.9k ★) | Search + extract + map + crawl as MCP tools | API-key based | "Search and extraction without rolling your own" |

The exception: Crawl4AI runs a real Chromium under the hood, so it does render JS. It's listed here because the *agent-facing* surface is "URL in, markdown out" — the agent doesn't drive the browser.

**Two shapes within Tier 1: compressing vs raw markdown.**

The tools split into two camps based on what comes back:

- *Compressing* — `WebFetch`, `crwl -q "..."`, Tavily extract. A small model reads the page and returns only its summary. Bounded, predictable token cost.
- *Raw markdown* — Jina Reader, `crwl -o markdown`. Full page text, no summarization. You filter yourself.

Concrete numbers, same URL (`github.com/microsoft/playwright-mcp` README):

| Tool | Output | ~Tokens into your context |
| --- | --- | --- |
| `WebFetch` (3-sentence summary prompt) | ~370 chars | ~90 |
| `WebFetch` (detailed extraction prompt) | ~2k chars | ~500 |
| Jina Reader (`r.jina.ai/<url>`) | ~55k chars | ~13,700 |
| `crwl -o markdown` | similar to Jina | ~10–14k |
| `WebSearch` (per call, `max_uses=5`) | result blobs only | ~5–15k |

The ~150x WebFetch-vs-Jina gap is real and compounds. Twenty fetches at 200 tokens each is 4k; twenty fetches at 13k each is 260k — the difference between staying in your context window and blowing it.

The catch: WebFetch's saving comes from delegating extraction to a small fast model. If your prompt is vague ("summarize this page"), the small model picks what to keep — you may miss the detail you actually wanted. The fix is a sharp prompt ("Extract X, Y, Z verbatim"), not a different tool.

**Practical implication:** default to the compressing camp for research. Escalate to raw markdown only when (a) `WebFetch` fails — auth walls, redirects, 402s — or (b) you specifically don't trust the small model's filtering. `WebSearch` is its own category, and the newer `web_search_20260209` version lets Claude write code to filter results before they hit context, which is worth enabling for any session with many searches.

**Where Tier 1 falls over:**

- Login-walled content (paywalled articles, internal tools, social platforms).
- SPAs where useful content only appears after user interaction (filters, dropdowns, infinite scroll).
- Cloudflare / PerimeterX / DataDome challenge pages — most Tier 1 tools either fail or get a stub.
- Anything that requires *doing* something — submitting a form, completing a checkout, posting a comment.

**Key takeaway:** Tier 1 is where 70–80% of agent web work should happen. It's read-only (small blast radius), cheap, and fast. If you can answer the question by reading a URL, do that and stop.

## Tier 2: Deterministic browser

**The job:** drive a real browser through scripted actions — navigate, click, fill, screenshot — without involving an LLM in the inner loop.

**The tools:**

| Tool | Stars | Approach | Notable |
| --- | --- | --- | --- |
| [Playwright MCP][7] (Microsoft) | 31.8k | Accessibility tree, not pixels | Default for most coding agents |
| [chrome-devtools-mcp][8] (Google) | 37.7k | Chrome DevTools Protocol | Adds debugging, network inspection, perf traces |
| [Browser MCP][9] | — | Drives your real browser via extension | Inherits your logins and profile |
| gstack `browse` | — | Headless Chromium, ~100ms / command | Optimized for fast individual commands; QA flavor |
| Hand-coded Playwright / Puppeteer | — | Direct script | Fastest at runtime; brittle to site changes |

**The accessibility-tree win.** This is the single most important architectural choice in Tier 2. Playwright MCP and similar tools serialize the browser's *accessibility tree* — a structured semantic representation of the page — instead of pixels. "An accessibility snapshot averages 2 to 5KB. A screenshot of the same page runs 100KB or more. That's a 20x to 50x difference in token cost." [[2]] Agents that operate on the accessibility tree are also more reliable, because they're matching on roles and labels rather than pixel coordinates that shift with every CSS change.

**The MCP context-bloat trap.** A subtler tradeoff: MCP servers stream the full accessibility snapshot back to the LLM in the tool response after every action. By step 15 of a flow, your context carries 60–80k tokens of stale page state from screens the agent already left. Morphllm benchmarked this against the Playwright *CLI* (which writes snapshots to disk and lets the agent read them on demand): 27k tokens per task with the CLI vs 114k with MCP — about 4x cheaper [[10]]. The Playwright team's published guidance: "If your agent has filesystem access, use CLI. If it's sandboxed, use MCP." Worth knowing if you're paying per token at scale.

**Speed numbers** (from the NxCode comparison [[1]]):

| Action | Playwright | Stagehand | Browser Use |
| --- | --- | --- | --- |
| Click button | <100 ms | 1–3 s | 2–5 s |
| Form fill (5 fields) | <500 ms | 5–15 s | 10–30 s |
| Single-page extraction | <200 ms | 2–8 s | 5–15 s |

Playwright wins on speed by an order of magnitude *because there is no LLM in the loop*. The cost is brittleness — selectors break when the page changes, and you need a human (or a Tier 3 tool) to fix them.

**Where gstack fits.** gstack `browse` is a Tier 2 tool — fast, deterministic, command-oriented. The companion skill `connect-chrome` opens a visible Chromium with anti-bot stealth built in, which puts it on the boundary between Tier 2 and the anti-bot infrastructure described below. If you're using gstack for QA-style work (dogfooding flows, screenshot diffing, regression checks), Tier 2 is where it belongs.

**Key takeaway:** Tier 2 is the right answer when you know the steps and the site is stable enough to write a script for. The accessibility-tree advantage is real and quantitative — don't pick a screenshot-based tool unless you actually need vision (e.g. canvas-rendered apps, charts, sites with broken accessibility).

## Tier 3: AI-driven action

**The job:** hand the LLM the steering wheel. The model observes the page, picks the next action, and the loop repeats until the task is done.

**The tools:**

| Tool | Stars | Architecture | When it fits |
| --- | --- | --- | --- |
| [Stagehand][11] (Browserbase) | 22.4k | Playwright + AI primitives (`act`, `extract`, `observe`); auto-caches successful selectors | TypeScript shops augmenting existing Playwright suites |
| [Browser Use][12] | 91.2k | Full autonomous Python agent loop; LLM reasons every step | Open-ended tasks where steps can't be predicted |
| [Skyvern][13] | 21.4k | Vision LLM + swarm of agents, no DOM dependency | Novel sites, broken accessibility, sites where DOM lies |
| Anthropic Computer Use | beta | Screenshot + mouse/keyboard control | Desktop apps, canvas UIs, when DOM doesn't help |

**Three different bets.** Stagehand bets that the dynamic part of any flow is small, so cache the successful actions and replay them deterministically — only call the LLM when the page changed. Browser Use bets the LLM should reason on every step because the world is messier than that. Skyvern and Computer Use bet the DOM is unreliable enough that vision is the right primitive.

**Be careful with the WebVoyager numbers.** Different sources publish very different reliability claims for the same tool — Browser Use is reported at 89.1% on WebVoyager in one comparison [[14]] and at 72–78% in another [[1]], and HN practitioners have reported success rates closer to 20–40% in less optimal configurations [[15]]. The benchmark number depends heavily on the model paired with the agent (GPT-4.1 vs Claude Opus), the specific WebVoyager subset, and whether the run uses optimized prompting. A useful read is: ceiling is high when you tune everything, variance is high in the wild.

**Cost numbers** (from NxCode [[1]]):

| Tool | Per-task cost |
| --- | --- |
| Playwright (no LLM) | \$0 |
| Stagehand `act()` | ~\$0.002–0.01 |
| Stagehand `extract()` | ~\$0.005–0.02 |
| Browser Use, simple (5 steps) | ~\$0.02–0.08 |
| Browser Use, complex (20 steps) | ~\$0.08–0.30 |

**Maintenance numbers, 30-day window on live sites:** Playwright scripts needed selector fixes on 15–25% of flows. Stagehand and Browser Use needed prompt adjustments on under 5% [[1]]. The AI tier pays for itself when site change is the dominant cost.

**Key takeaway:** Tier 3 is the right answer when steps are dynamic, sites change, or the task is genuinely open-ended ("book me the cheapest flight to Tokyo next month"). It's the wrong answer for stable known flows — you're paying 100x the cost and accepting much higher variance.

## Cross-cutting: anti-bot infrastructure

This sits orthogonal to the three tiers — it can wrap Tier 1, 2, or 3 transparently. The tools:

| Tool | Stars | What it solves |
| --- | --- | --- |
| [Browserbase][16] | — | Managed stealth Chromium fleet, residential proxies, CAPTCHA, MFA. "85% APIs can't reach" [[17]] |
| [Firecrawl][18] | 113k | Markdown-out API with rotating proxies, JS rendering; AGPL self-host or cloud |
| ScrapingBee / ScraperAPI / Bright Data | — | Pure proxy + rendering as a service |

These exist because raw `curl`, raw Playwright, and even Playwright in headless mode get blocked on a meaningful slice of the web. Cloudflare's bot-management products fingerprint TLS handshakes, browser builds, mouse-movement entropy, and a dozen other signals. If you control the site you're hitting, you don't need this. If you don't, it's the difference between "works in dev" and "works in production at 10k req/day."

**Pick by what you're being blocked on:**

- *Blocked at TLS / fingerprint level* → Browserbase or Bright Data
- *Need clean markdown at scale, not interaction* → Firecrawl
- *Just need a residential IP* → ScraperAPI / SerpAPI

## Safety: the prompt-injection problem

Every tier above Tier 1 shares a structural problem: **anything the agent reads can become an instruction it follows.** This is indirect prompt injection, and it is not a hypothetical.

OpenAI's own position, from a December 2025 blog post on Atlas browser security:

> "Prompt injection, much like scams and social engineering on the web, is unlikely to ever be fully 'solved.'" [[19]]

Brave's writeup of an indirect-injection attack on Perplexity Comet — where an attacker hid instructions in webpage content that caused the AI to extract the user's email, request an OTP, and exfiltrate via a Reddit comment — concludes:

> "Traditional protections such as same-origin policy (SOP) or cross-origin resource sharing (CORS) are all effectively useless." [[20]]

The real-world picture: Google reported a 32% relative increase in malicious indirect-injection content in CommonCrawl scans between November 2025 and February 2026 [[21]]. Page-summarization features have been measured at a 73% attack success rate, and question-answering features at 71% [[22]]. Forcepoint's framing of risk-by-capability is the cleanest:

> "A browser AI that can only summarize is low-risk. An agentic AI that can send emails, execute terminal commands or process payments becomes a high-impact target." [[21]]

**Practical mitigations a CLI agent can apply today:**

1. **Default to Tier 1.** A read-only fetch into context can be poisoned, but it can't *do* anything by itself. The damage is bounded by what other tools the agent has.
2. **Domain allowlists on Tier 2 and 3.** Most agent harnesses support `allowed_domains`. Use it for any flow that touches authenticated services.
3. **Schema-constrained tools.** Don't expose `browser_execute_js` or shell-like primitives to a Tier 3 agent unless you have to. Constrain the action space.
4. **Sandbox per origin.** A Tier 3 agent that needs to log in should run in a fresh ephemeral profile, not your real one. Browserbase's "identity" product does this; rolling your own with Playwright contexts works too.
5. **Human-in-the-loop on irreversible actions.** Anthropic's Computer Use docs explicitly recommend "asking a human to confirm decisions that may result in meaningful real-world consequences" [[23]]. Same logic applies to any Tier 3 tool.

**Key takeaway:** the security model isn't "lock down the LLM"; it's "minimize what the LLM can do on the user's authority." The lower on the axis you can do the work, the smaller the blast radius if a page is hostile.

## The "best combination" matrix

Five concrete combinations for common CLI-agent shapes. The dominant axis is *what the agent is for*, not which tool is fashionable this month.

### Combination A — Research / RAG agent

> **Use when:** the agent answers questions, summarizes documents, fact-checks, or builds knowledge bases.

```text
WebSearch  →  WebFetch / Jina Reader  →  Crawl4AI (offline batches)
   ↓               ↓                         ↓
search results   read individual URLs    bulk-ingest a domain
```

- **Why:** read-only, cheap, low blast radius. The whole agent can run without ever touching Tier 2 or 3.
- **Cost order:** \$0.01–0.05 per query.
- **What this very blog post used.** The research for this draft was Combination A — WebSearch for the landscape scan, WebFetch on each primary source.

### Combination B — Coding / dev agent

> **Use when:** the agent is a software engineering assistant (Claude Code, Cursor, Copilot CLI) that needs to look at docs, GitHub issues, error pages.

```text
WebFetch  →  Playwright MCP or chrome-devtools-mcp (when needed)
   ↓                  ↓
docs lookup    debugging, perf traces, JS-heavy sites
```

- **Why:** WebFetch handles 90% of "look up the API for X" cases; the deterministic browser handles the rest.
- **Cost order:** WebFetch is free in usage terms; the MCP browser is \$0 LLM cost per click.
- **Skip Tier 3** unless you're specifically building a QA agent. Coding agents rarely need to *act* on websites.

### Combination C — Web QA / regression pipeline

> **Use when:** running automated tests against a live site you control.

```text
Playwright (deterministic, scripted)  +  Stagehand for the dynamic 20%
        ↓                                    ↓
80% of the suite                        flakey selectors, dynamic forms
```

- **Why:** keep cost flat for known flows; pay LLM cost only when sites change. The 30-day maintenance numbers favor this hybrid: scripts cover the stable core, AI fills in for drift [[1]].
- **gstack `browse` slots in here** as the deterministic side if you're already in that ecosystem.

### Combination D — Open-ended operator agent

> **Use when:** the agent is asked to *do* things in the world — book travel, file forms, complete checkouts, navigate sites it's never seen.

```text
Browser Use or Computer Use  +  Browserbase (or Steel)  +  sandboxed profile
            ↓                              ↓                        ↓
LLM-driven action loop           anti-bot, residential IP     ephemeral, scoped auth
```

- **Why:** novel sites need vision or DOM-AI; bot detection needs stealth infra; auth needs isolation per task.
- **Cost order:** \$0.05–0.50 per task plus infra.
- **Risk note:** this is the highest-blast-radius combination in the post. Treat it like running untrusted code: ephemeral profiles, no real credentials, no payment instruments without explicit user confirmation per action.

### Combination E — High-volume scrape / RAG ingestion

> **Use when:** the workload is "turn this list of 50,000 URLs into clean markdown."

```text
Firecrawl (or Crawl4AI self-hosted)  →  fallback to Jina Reader on failures
              ↓                                     ↓
managed proxy + JS render             cheap unblocking for soft fails
```

- **Why:** Firecrawl handles the hard cases (JS, anti-bot) at scale; Jina Reader is a free fallback for the easy cases. Self-hosting Crawl4AI is the cost-control option once volume justifies it.

## Common pitfalls

- **Reaching for Tier 3 when Tier 1 would do.** The most expensive bug in this space is "let me have my agent open a browser and search Google" when WebSearch returns the same answer in one call.
- **Treating MCP as the default when CLI is cheaper.** If your agent has filesystem access (most coding agents do), the Playwright CLI is roughly 4x cheaper than the MCP server on the same task [[10]]. Pick MCP when you're sandboxed, not by reflex.
- **Trusting any single benchmark number.** Browser Use reported at 89.1%, 78%, 72%, and "20–40% in our setup" by different sources is the same tool measured differently. Always check what model and harness is paired with the agent.
- **Forgetting the agent is now part of your control plane.** Once an agent browses on your auth, the data it reads is the data that decides what it does. SOP and CORS were designed for users, not autonomous browsers.
- **Skipping the anti-bot wrapper until production.** "Works on my machine" almost always means "the site hasn't fingerprinted my dev IP yet." Test against the production proxy stack you'll actually deploy with.

> **Try it yourself:** pick a single page with a clear answer (a Wikipedia article, an OG-tagged blog post). Have your agent answer the same question via (a) WebFetch, (b) Playwright MCP `browser_navigate` + `browser_snapshot`, and (c) a Browser Use agent. Log token cost and wall-clock latency for each. The 10–100x gap will be obvious. That gap is the cost of climbing the axis — only pay it when the lower tier can't do the job.

## References

[1]: https://www.nxcode.io/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026
[2]: https://dev.to/stevengonsalvez/browser-tools-for-ai-agents-part-1-playwright-puppeteer-and-why-your-agent-picked-playwright-k71
[3]: https://platform.claude.com/docs/en/docs/build-with-claude/tool-use/web-search-tool
[4]: https://jina.ai/reader/
[5]: https://github.com/unclecode/crawl4ai
[6]: https://github.com/tavily-ai/tavily-mcp
[7]: https://github.com/microsoft/playwright-mcp
[8]: https://github.com/ChromeDevTools/chrome-devtools-mcp
[9]: https://browsermcp.io/
[10]: https://www.morphllm.com/playwright-mcp
[11]: https://github.com/browserbase/stagehand
[12]: https://github.com/browser-use/browser-use
[13]: https://github.com/Skyvern-AI/skyvern
[14]: https://awesomeagents.ai/tools/best-ai-browser-automation-tools-2026/
[15]: https://news.ycombinator.com/from?site=browser-use.com
[16]: https://www.browserbase.com/
[17]: https://www.browserbase.com/
[18]: https://github.com/firecrawl/firecrawl
[19]: https://techcrunch.com/2025/12/22/openai-says-ai-browsers-may-always-be-vulnerable-to-prompt-injection-attacks/
[20]: https://brave.com/blog/comet-prompt-injection/
[21]: https://www.helpnetsecurity.com/2026/04/24/indirect-prompt-injection-in-the-wild/
[22]: https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/
[23]: https://platform.claude.com/docs/en/docs/agents-and-tools/computer-use

1. NxCode, *Stagehand vs Browser Use vs Playwright: AI Browser Automation Compared (2026)* [[1]]
2. Steven Gonsalvez, *Browser Tools for AI Agents Part 1: Playwright, Puppeteer, and Why Your Agent Picked Playwright* [[2]]
3. Anthropic, *Web search tool* documentation [[3]]
4. Jina AI, *Reader* [[4]]
5. unclecode, *Crawl4AI* (64.8k ★) [[5]]
6. tavily-ai, *Tavily MCP* (1.9k ★) [[6]]
7. Microsoft, *Playwright MCP* (31.8k ★) [[7]]
8. ChromeDevTools, *chrome-devtools-mcp* (37.7k ★) [[8]]
9. Browser MCP [[9]]
10. Morphllm, *Playwright MCP Setup and Cost: Why the CLI Is 4x Cheaper* [[10]]
11. Browserbase, *Stagehand* (22.4k ★) [[11]]
12. browser-use, *Browser Use* (91.2k ★) [[12]]
13. Skyvern-AI, *Skyvern* (21.4k ★) [[13]]
14. Awesome Agents, *AI Browser Automation in 2026: Top 6 Tools Compared* [[14]]
15. Hacker News submissions from browser-use.com [[15]]
16. Browserbase landing page [[16]]
17. Browserbase, scale claims [[17]]
18. firecrawl, *Firecrawl* (113k ★) [[18]]
19. TechCrunch, *OpenAI says AI browsers may always be vulnerable to prompt injection attacks* [[19]]
20. Brave, *Agentic Browser Security: Indirect Prompt Injection in Perplexity Comet* [[20]]
21. Help Net Security, *Indirect prompt injection is taking hold in the wild* (Google CommonCrawl scan stats; Forcepoint capability quote) [[21]]
22. Unit 42 (Palo Alto Networks), *Fooling AI Agents: Web-Based Indirect Prompt Injection Observed in the Wild* [[22]]
23. Anthropic, *Computer use tool* documentation [[23]]

Star counts captured April 2026 and will go stale.
