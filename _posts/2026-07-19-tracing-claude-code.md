---
layout: post
title: "Tracing Claude Code: Four Ways to See What Your Agent Is Doing"
categories: [AI Coding, LLMs, Agents, Observability]
excerpt: "A survey of tools for tracing Claude Code - local log viewers, API interceptors, native OpenTelemetry, and eval platforms like Langfuse and Braintrust. The capture mechanism you pick decides what you can see, whether it scales to a team, and whether you can close an eval loop."
---

TL;DR - Claude Code is a black box until you point something at it. The tools that open it up split into four families by *how they capture data*: **local log viewers** read the JSONL transcripts Claude Code already writes; **API interceptors** monkey-patch the network layer to grab the raw request/response (including the system prompt); **native OpenTelemetry** emits metrics and events to any OTLP backend; and **eval platforms** register hooks that forward structured traces and add an evaluation loop. The right system for you depends on whether you want local observability, large-scale observability, or a platform with eval integration. This post surveys the landscape of observability tools in mid-2026.

## Table of Contents <!-- omit from toc -->

- [Why the capture mechanism matters](#why-the-capture-mechanism-matters)
- [Family 1: Local log viewers](#family-1-local-log-viewers)
- [Family 2: API interceptors](#family-2-api-interceptors)
- [Family 3: Native OpenTelemetry](#family-3-native-opentelemetry)
- [Family 4: Eval platforms](#family-4-eval-platforms)
- [General-purpose LLM observability: proxies and OTEL SDKs](#general-purpose-llm-observability-proxies-and-otel-sdks)
- [The comparison table](#the-comparison-table)
- [How to choose](#how-to-choose)
- [References](#references)

## Why the capture mechanism matters

Tracing tools for Claude Code vary across three dimensions:

1. **Content depth.** How much of the interaction can the tool actually see? At one end is the raw API payload - system prompt, every tool definition, and thinking blocks. At the other are aggregate counters: tokens, cost, tool-accept rates, with the prompt text redacted by default.
2. **Scale.** Does it watch one session on your laptop, or a whole team's fleet with dashboards and alerting?
3. **Feedback loop.** Is the captured data a dead end you read once, or can it flow back into evals, experiments, and prompt iteration?

The tools with the deepest view - interceptors reading raw API traffic - are the hardest to run for a whole team, while the one that scales cleanest to a fleet, OpenTelemetry, redacts content by default. The eval platforms carve out a middle: full-transcript depth at team scale, though still not the raw system prompt an interceptor sees.

## Family 1: Local log viewers

Claude Code already writes a full transcript of every session to `~/.claude/projects/<encoded-project-path>/<session-id>.jsonl`, containing the full conversation, tool calls, token usage, etc. The format isn't officially documented, but it's newline-delimited JSON you can inspect directly - one object per line. Local viewers parse those logs into something readable on your machine. Because that transcript is written for every session automatically, you can **inspect a run that already happened** - even one you never intended to trace.

**[claude-code-trace](https://github.com/delexw/claude-code-trace)** [[1]] (delexw, MIT, ~352★ at time of writing) is a Claude Code session log viewer with a GUI. It discovers your sessions automatically, renders conversations with expandable tool calls, shows token counts and timestamps, decodes MCP tool names into human-friendly labels (`mcp__chrome-devtools__take_screenshot` becomes "MCP chrome-devtools · take screenshot"), and can live-tail an active session. It ships a desktop app, a web app, and a TUI. Claude-code-trace is free and open source, and can run locally on your machine.

**[vexorkai/claude-trace](https://github.com/vexorkai/claude-trace)** [[2]] is a CLI that reads the same logs and focuses on surfacing token-usage breakdowns by session, tool, project, and timeline. It surfaces session costs and the most expensive tools/skills/actions:
```text
Tools by attributed cost
tool                 calls    cost       avg/call   % of total
Read                 1142     $436.894   $0.383      56%  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓
Bash                 1482     $132.756   $0.090      17%  ▓▓▓▓
Task                 64       $123.095   $1.923      16%  ▓▓▓▓
Write                321      $22.887    $0.071       3%  ▓ 
```

Local logs already contain most of what you need to inspect model and harness **behavior** - you can answer "why did these tools get called?" or "did a particular skill get invoked?" And if an open-source CLI is missing something, you can ask Claude to customize it. What the logs don't hold is the system prompt and thinking blocks; to see those you need an API interceptor.

## Family 2: API interceptors

To capture the system prompt, the full tool schemas, the thinking blocks - you have to catch the request before it leaves your machine. Interceptors do this by monkey-patching `global.fetch` and Node's HTTP library, then launching Claude Code with the patch injected.

**[mariozechner/claude-trace](https://www.npmjs.com/package/@mariozechner/claude-trace)** [[3]] logs every request/response pair to `.claude-trace/` and builds a self-contained HTML viewer - no server needed - with thinking blocks, a token/cache breakdown, and a debug view of every HTTP call. This is the level at which you can see the harness work: trace a session and you can watch the `dispatch_agent` tool spawn sub-agents that call other models, a pattern that burns through tokens fast [[4]]. That's the interceptor's niche: understand *how Claude Code itself works*, reverse-engineer the harness, or debug something the transcript doesn't explain.

**[claude-tap](https://github.com/liaohch3/claude-tap)** [[5]] takes the same interception approach but casts a wider net - it inspects API traffic from Claude Code, Codex CLI, Gemini CLI, Cursor CLI, and several other agents in one local viewer. Useful if you're comparing harnesses rather than living in one.

The tradeoff mirrors the local viewers: maximum content depth, but it stays local and per-session. And because you're launching Claude Code through a wrapper, **you only capture sessions you decided to trace in advance** - there's no reading back a run you didn't wrap, the way a log viewer lets you.

Both session logs and interceptor outputs land in your working directory. Great for a debugging session; not a fleet-monitoring story.

## Family 3: Native OpenTelemetry

Claude Code has OpenTelemetry instrumentation built in. Set `CLAUDE_CODE_ENABLE_TELEMETRY=1`, point it at an OTLP endpoint, and it emits telemetry to any compatible backend - SigNoz, Datadog, Honeycomb, Grafana, Elastic, or a self-hosted collector [[6]].

Of the four families, this is the one that scales to a whole team. Because it relies on the same OpenTelemetry instrumentation you'd already point at a production service, a platform team doesn't have to stand up anything new - they can route Claude Code's telemetry into whatever monitoring stack they already run. That telemetry arrives as metrics, events, and the attributes attached to each [[6]]:

- **Metrics:** token usage (input/output/cache), estimated USD cost, session counts, lines of code, commits, PRs, tool accept/reject decisions, active usage time.
- **Events:** user prompts, API requests and errors, tool results and decisions, permission-mode changes, plugin/skill activation, auth events.
- **Attributes on every signal:** session ID, user ID, email, org, terminal type, app version.

Native OpenTelemetry deliberately trades away content depth. Prompts are **redacted by default** - capturing full prompt text requires opting in with `OTEL_LOG_USER_PROMPTS=1`, and even then it emits metrics and structured events rather than full response bodies [[6]]. That's the right default for a team deployment: you don't want every engineer's prompts landing in a shared observability store by accident. This means OTEL answers "how much is the team spending and where are tools failing?" far better than "what exactly did Claude say in this session?"

Around this native export sits an ecosystem of pre-built stacks. **[ColeMurray/claude-code-otel](https://github.com/ColeMurray/claude-code-otel)** [[7]] packages a full monitoring setup. Vendors have written integration guides - [SigNoz](https://signoz.io/docs/claude-code-monitoring/) [[6]], [General Analysis](https://generalanalysis.com/guides/claude-code-control-observability-opentelemetry) [[8]] - and Elastic frames it as a security/SIEM problem: monitoring Claude Code across an org as an audit and threat-detection surface [[9]]. Same underlying telemetry, different backend and different question.

## Family 4: Eval platforms

The last family works through hooks - Claude Code's lifecycle hooks (`SessionStart`, `UserPromptSubmit`, `Stop`, and so on) fire scripts at defined points, and these platforms register scripts that forward structured traces to a backend. What sets them apart is that tracing is the *front door* to an evaluation and experimentation product, not the whole product.

**[Langfuse](https://langfuse.com/integrations/developer-tools/claude-code)** [[10]] registers a `Stop` hook that runs after each response, reads the conversation transcript, and converts it into hierarchical traces - turn traces containing generation spans, with tool spans nested underneath. It captures prompts, responses, tool inputs/outputs, timing, and token/cache metrics, grouped by `session_id`. Langfuse is open-source: you can self-host it for free or use their cloud tier, so it doesn't fit cleanly into a "free vs paid" split - it's both, depending on how you run it. Tracing is a small part of Langfuse: it also handles prompt management, datasets, and evals, plus an Agent Skill / MCP server that lets Claude Code query its own production data from the terminal.

**[Braintrust](https://www.braintrust.dev/blog/claude-code-braintrust-integration)** [[11]] ships two plugins [[12]], one for each direction the data flows. The first, `trace-claude-code`, captures every session as hierarchical traces automatically - each session becomes one trace, with turns and tool calls as child spans, and the token counts are stated to match Claude Code's own `/usage` exactly. The second, `braintrust`, runs the data the *other* direction: it lets you query logs, pull experiment results, and log new examples from inside the terminal via MCP.

That bidirectional idea is the real differentiator of this family. A local viewer or an OTEL dashboard is somewhere you *go* to look at data. The eval platforms want the data to come back to where you're already working - so you can pull a failing case, add it to a dataset, and rerun an eval without leaving the editor. Whether that's worth adopting a platform depends on whether you're doing enough systematic evaluation to justify it; for pure "what happened in this session?" debugging, it's more machinery than the job needs.

## General-purpose LLM observability: proxies and OTEL SDKs

Two general-purpose LLM observability tools also apply here, from opposite ends of the stack:

**[Helicone](https://github.com/Helicone/helicone)** [[13]] is a proxy. You point Claude Code's API base URL at Helicone's Anthropic gateway (`ANTHROPIC_BASE_URL=https://anthropic.helicone.ai/v1`, plus your Helicone key), and every request flows through Helicone on its way to Anthropic. It logs the full request and response, tracks tokens and cost, and can cache responses and rate-limit before forwarding. Because it captures at the network boundary instead of on your machine, it sees raw Anthropic API calls - not Claude Code's sessions, tools, or skills - and it captures any other provider you route through it the same way.

**[Traceloop / OpenLLMetry](https://github.com/traceloop/openllmetry)** [[14]] is the third-party cousin of Family 3: an open-source set of OpenTelemetry instrumentations for LLM calls, with pre-built support for Anthropic, OpenAI, LangChain, and others. It auto-instruments the model calls *your own code* makes, turning prompts, completions, and token usage into OTEL spans you can export to Datadog, Honeycomb, or any OTLP backend. That makes it a fit when you're building on the Claude Agent SDK and want to trace your app's calls - not when you're running the Claude Code CLI, whose process you don't instrument.

These general-purpose tools work well beyond Claude Code. They're the right choice when you're running other LLM setups alongside it, e.g., a production app using OpenAI APIs or LangChain, and want to watch everything in one place.

## The comparison table

| Tool | Capture mechanism | Content depth | Scale | Hosting | Eval loop |
|------|-------------------|---------------|-------|---------|-----------|
| [claude-code-trace](https://github.com/delexw/claude-code-trace) | Reads local JSONL | Transcript (turns + tools) | Single session | Local, no account | No |
| [mariozechner/claude-trace](https://www.npmjs.com/package/@mariozechner/claude-trace) | Intercepts API `fetch` | Raw payload (system prompt, thinking) | Single session | Local, no account | No |
| [claude-tap](https://github.com/liaohch3/claude-tap) | Intercepts API (multi-agent) | Raw payload | Single session | Local, no account | No |
| Native OTEL → [SigNoz](https://signoz.io/docs/claude-code-monitoring/) / Datadog / Elastic | Built-in OTLP export | Metrics + events (prompts redacted by default) | Team / fleet | Self-host or SaaS | Via backend |
| [Langfuse](https://langfuse.com/integrations/developer-tools/claude-code) | Lifecycle hooks | Transcript traces | Solo → team | Self-host (free) or cloud | Yes |
| [Braintrust](https://www.braintrust.dev/blog/claude-code-braintrust-integration) | Lifecycle hooks + MCP | Transcript traces | Solo → team | SaaS | Yes (bidirectional) |
| [Helicone](https://github.com/Helicone/helicone) | Proxy in front of API | Full request/response | Solo → team | Self-host or cloud | Partial |

## How to choose

The families sort cleanly by what you're trying to do:

- **Debug one session, or understand how Claude Code works internally.** Start local. A log viewer like claude-code-trace if you want a readable conversation with tool calls; vexorkai/claude-trace if the question is cost attribution by tool; an interceptor like mariozechner/claude-trace if you specifically need the system prompt, tool schemas, or thinking blocks the transcript hides. Zero signup, nothing leaves your machine.
- **Track cost and usage across a team.** Native OpenTelemetry into whatever backend your org already runs. It's the standard-infrastructure path, it aggregates across engineers, and its content-redaction default is a feature, not a limitation, for a shared store. Elastic's framing is worth a look if the driver is audit/security rather than cost.
- **Systematically evaluate and improve agent behavior.** An eval platform. Langfuse if you want the option to self-host and an open-source ecosystem; Braintrust if the bidirectional, query-from-the-terminal workflow fits how your team works. Both give you traces *plus* the machinery to turn a bad session into a test case.

The families aren't mutually exclusive. Practically, a team may run an interceptor or local viewer for hands-on debugging *and* native OTEL for fleet cost tracking, because each tool answers fundamentally different questions.

## References

- [[1]] delexw, *claude-code-trace* - [github.com/delexw/claude-code-trace](https://github.com/delexw/claude-code-trace)
- [[2]] vexorkai, *claude-trace* (token-usage CLI) - [github.com/vexorkai/claude-trace](https://github.com/vexorkai/claude-trace)
- [[3]] mariozechner, *claude-trace* - [npmjs.com/package/@mariozechner/claude-trace](https://www.npmjs.com/package/@mariozechner/claude-trace)
- [[4]] Simon Willison, "claude-trace" - [simonwillison.net/2025/Jun/2/claude-trace/](https://simonwillison.net/2025/Jun/2/claude-trace/)
- [[5]] liaohch3, *claude-tap* - [github.com/liaohch3/claude-tap](https://github.com/liaohch3/claude-tap)
- [[6]] SigNoz, "Claude Code Monitoring with OpenTelemetry" - [signoz.io/docs/claude-code-monitoring/](https://signoz.io/docs/claude-code-monitoring/)
- [[7]] ColeMurray, *claude-code-otel* - [github.com/ColeMurray/claude-code-otel](https://github.com/ColeMurray/claude-code-otel)
- [[8]] General Analysis, "Claude Code Control and Observability with OpenTelemetry" - [generalanalysis.com/guides/claude-code-control-observability-opentelemetry](https://generalanalysis.com/guides/claude-code-control-observability-opentelemetry)
- [[9]] Elastic Security Labs, "Claude Code/Cowork monitoring at scale with Otel & Elastic" - [elastic.co/security-labs/claude-code-cowork-monitoring-otel-elastic](https://www.elastic.co/security-labs/claude-code-cowork-monitoring-otel-elastic)
- [[10]] Langfuse, "Claude Code Tracing with Langfuse" - [langfuse.com/integrations/developer-tools/claude-code](https://langfuse.com/integrations/developer-tools/claude-code)
- [[11]] Braintrust, "Claude Code meets Braintrust" - [braintrust.dev/blog/claude-code-braintrust-integration](https://www.braintrust.dev/blog/claude-code-braintrust-integration)
- [[12]] braintrustdata, *braintrust-claude-plugin* - [github.com/braintrustdata/braintrust-claude-plugin](https://github.com/braintrustdata/braintrust-claude-plugin)
- [[13]] Helicone - [github.com/Helicone/helicone](https://github.com/Helicone/helicone)
- [[14]] Traceloop, *OpenLLMetry* - [github.com/traceloop/openllmetry](https://github.com/traceloop/openllmetry)
