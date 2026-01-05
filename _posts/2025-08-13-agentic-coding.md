---
layout: post
title:  Agentic Code Development with Claude Code
categories: [AI Coding, LLMs, LLM Toolchain]
---

Early users treated LLMs as one-shot text generators. Users focused on clever wording, examples, and formatting of their prompts to achieve their goals. This became known as "prompt engineering". Prompt Engineering worked for simple tasks, but broke down as soon as people needed memory, tools, retrieval, or multi-step reasoning.

As systems became stateful, tool-using, and long-running, it became clear that model behavior was driven less by phrasing and more by what information was present, structured, ordered, and refreshed over time. The problem shifted from “How do I word this prompt?” to “What context should the model see at this moment, and why?”

That shift—managing instructions, state, memory, retrieved knowledge, and tool outputs across interactions—is what became known as context engineering.

Claude Code runs an agentic loop: you submit a prompt → Claude chooses tools → executes them → responds. Within this loop, Claude can invoke two context context management tools: **subagents** (isolated AI instances with specialized instructions) or **skills** (prompt templates that enhance the current conversation). Understanding when to use each is the key to production-quality agentic development. This post goes into the main principles of these tools, and parctical tips on getting started with them.

## Subagents
Subagents are specialized, short-lived agents that each receive a tightly scoped slice of context to perform a specific task (e.g., search, refactor, test, or analyze) independently. Their outputs are then merged back into the main agent’s context, allowing complex coding workflows to scale without overwhelming a single prompt or context window.

Claude Code parses the user's prompt to infer intent, then calls the appropriate subagent as it would other tools. Each time a subagent is triggered, it:
1. Starts with a blank context window
2. Loads the project's `CLAUDE.md` file
3. Loads its own set of focused instructions
4. Receives specific context from the main agent

Based on this workflow, a cluttered `CLAUDE.md` risks degrading the performance of your subagents. For this reason, `CLAUD.md` should be kept lean. With subagents, you can split up a large, cluttered `CLAUDE.md` into specific instructions for specific agents - planning, reviewing, styling, committing, etc. You could build your own agents, but I recommend starting with pre-built ones that have already been battle tested. Claude Code already comes with pre-defined agents -- for example, the `plan` mode uses a Plan subagent.

### Under the Hood
Subagents are defined as markdown files that live in `.claude/agents/`. Like general AI agents, they have access to specific instructions and tools.

A simple subagent could look like:
```md
---
name: your-sub-agent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3  # Optional - inherits all tools if omitted
model: sonnet  # Optional - specify model alias or 'inherit'
permissionMode: default  # Optional - permission mode for the subagent
skills: skill1, skill2  # Optional - skills to auto-load
---

Your subagent's system prompt goes here. This can be multiple paragraphs
and should clearly define the subagent's role, capabilities, and approach
to solving problems.

Include specific instructions, best practices, and any constraints
the subagent should follow.
```
(from the docs: https://code.claude.com/docs/en/sub-agents)

During session start, Claude Code scans for available subagents. Then, during evaluation, Claude Code proactively delegates tasks to subagents based on:
* The task description in your request
* The description field in subagent configurations
* Current context and available tools
When this happens, the main agent will pass relevant context to the subagents

You can also explicitly invoke an agent by mentioning it in your command:
```
> ask the debugger subagent to investigate this error
```

## Where to Find Pre-Built Subagents

### Claude Code Plugin Marketplace (Recommended)

The easiest way to install pre-built subagents is through Claude Code's plugin system:

```bash
/plugins  # In Claude Code CLI - browse and install plugins
```

### Popular Community Collections

#### wshobson/agents ([GitHub](https://github.com/wshobson/agents))

A comprehensive production-ready system combining 99 specialized AI agents, 15 multi-agent workflow orchestrators, and 107 agent skills organized into 67 focused plugins. The repository is consistently cited in community resources as one of the top subagent collections.

**What the community says:**
- "Production-ready subagents for domains like RESTful API design and GraphQL schemas"
- Regularly recommended as the go-to "28-agent bundle" in developer guides
- Features 50 specialized subagents with each being an expert in a specific domain

**Notable agents:**
- `code-reviewer` - Security analysis with SonarQube, CodeQL, Semgrep integration
- `debugger` - Systematic error investigation with read-only permissions
- `architect-review` - Architectural design review and recommendations
- `test-runner` - Test execution with coverage reporting
- `doc-generator` - Automated documentation generation
- `commit-writer` - Semantic commit messages

**Installing via plugin:**
```bash
/plugin marketplace add wshobson/agents-marketplace
/plugin install agents@wshobson
```

#### VoltAgent/awesome-claude-code-subagents ([GitHub](https://github.com/VoltAgent/awesome-claude-code-subagents))

The most comprehensive reference repository for Claude Code subagents, featuring 100+ specialized AI agents for full-stack development, DevOps, data science, and business operations. As of early 2025, it has ~6.8k stars and is actively maintained by the community.

**What the community says:**
- "The most powerful Claude agents feel like hiring a team of experts—but you get code reviews, migrations, and tests done in minutes" ([source](https://dev.to/voltagent/100-claude-code-subagent-collection-1eb0))
- Featured on [awesomeclaude.ai](https://awesomeclaude.ai) as one of the key Claude resources
- "Performs comprehensive code reviews with the thoroughness of a senior engineer" - developers report catching subtle race conditions that would have caused production failures ([source](https://dev.to/necatiozmen/10-claude-code-subagents-every-developer-needs-in-2025-2ho))

**Most popular agents (by usage):**
- `fullstack-developer` - End-to-end features with type-safe APIs
- `code-reviewer` - Comprehensive code quality and security analysis
- `rust-engineer` - Memory-safe Rust development
- `platform-engineer` - Self-service infrastructure and GitOps
- `penetration-tester` - Security testing and vulnerability assessment
- `llm-architect` - RAG stacks and AI/ML pipeline design
- `refactoring-specialist` - Transform legacy code into clean architecture

**Organized by category:**
- **Architecture**: fullstack-developer, backend-architect, frontend-architect
- **DevOps**: platform-engineer, ci-cd-optimizer, incident-commander
- **Quality & Security**: code-reviewer, security-auditor, penetration-tester
- **Database**: db-optimizer, migration-generator, query-analyzer
- **Data Science**: llm-architect, data-engineer, ml-ops-specialist

Browse: https://github.com/VoltAgent/awesome-claude-code-subagents

### Best Practices from the Community

Based on [community recommendations](https://www.eesel.ai/blog/claude-code-subagents):
- **Design focused subagents**: Single, clear responsibilities work better than trying to make one subagent do everything
- **Create reproducible pipelines**: Use roles like Product Spec → Architect → Implementer/Tester for repeatable workflows
- **Start simple**: Generate initial subagents with Claude, then iterate to customize for your specific needs

### Manual Installation (Alternative)

If an agent isn't available as a plugin:

1. Download the `.md` file from the repository
2. Copy to `.claude/agents/` in your project root
3. Restart Claude Code to detect the new agent
4. Test: `ask the [agent-name] to...`


### Things to Consider: The Handoff Issue

When you invoke a subagent, the main agent passes only a summary of what it thinks the subagent needs—the subagent starts fresh with your `CLAUDE.md` file, its own instructions, and whatever context the main agent provides. This creates an information gap: nuanced decisions, discovered patterns, and architectural discussions from your conversation may get lost. If the main agents don't give subagents sufficient context, then the subagents will operate blindly and essentially "hallucinate".

This issue matters in scenarios like:
* Complex brownfield projects with deep architectural context spread across many files [https://www.eesel.ai/blog/subagents-in-claude-code]
* Large refactoring requiring understanding of intricate component relationships
* Tasks heavily dependent on conversation history built with the main agent
* When tasks are derived from nuanced design decisions that only exist in the conversation context

But this issue doesn't matter in scenarios like:
* Self-contained tasks: code review, testing, documentation—fresh eyes without implementation bias
* Specialized analysis: security audits, performance profiling benefit from isolated evaluation
* Greenfield projects with minimal accumulated context
* Tasks with clear boundaries that provide sufficient context in the request itself

Mitigation strategies:
1. **More detailed `CLAUDE.md`**: Put key architectural decisions, coding patterns, and constraints in this file since subagents load it
2. **Explicit context passing**: "Use the debugger and first explain the authentication flow, Redis caching strategy, and token refresh mechanism"
3. **Task(...) alternative**: Some developers prefer spawning general agent clones with `Task(...)`, which preserves more conversational context by cloning the general agent rather than spawning a specialized subagent. This trades specialization for context preservation.
4. **Strategic selection**: Choose subagents when isolation helps, use skills (see below) when context preservation matters

## Agent Skills
Rather than invoking subagents to carry out specific tasks, Anthropic introduced agent "skills" to conditionally inject additional context to the current conversation based on your instructions.

Skills are specialized prompt templates that inject domain-specific instructions into the conversation context. When a skill is invoked, it modifies both the conversation context (by injecting instruction prompts) and the execution context (by changing tool permissions and potentially switching the model). Instead of executing actions directly, skills expand into detailed prompts that prepare Claude to solve a specific type of problem. Each skill appears as a dynamic addition to the tool schema that Claude sees [https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/#:~:text=Claude%20Agent%20Skills%20Overview,on%20the%20skill%20descriptions%20provided.]

### Under the hood
Agent skills are simply folders that contain templates for subagents:
```
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

At the minimum, you need the `SKILL.md` file with something like:
```md
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

## Overview

[Essential instructions here]

## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)

## Utility scripts

To validate input files, run the helper script. It checks for required fields and returns any validation errors:

    python scripts/helper.py input.txt
```

What this means: with code template and scripts to run, we can give agents ways to access our environment - bash shell, our machine, ways to access .docx and .csv files, etc. We let agents write code on the fly to interact with these new file formats. This will increase the capabilities of what the agents are able to achieve.

Skills are the next evolution from MCPs -- Skills tell Claude how to use tools; MCP provides the tools. For example, an MCP server connects Claude to your database, while a Skill teaches Claude your data model and query patterns.

https://code.claude.com/docs/en/skills

## Subagents vs Skills: When to Use Which?

The key distinction: **Subagents run in isolation with their own context; Skills enhance the current conversation**.

**Use Subagents when you need:**
- **Isolated context** - Code review shouldn't see your work-in-progress from the main conversation
- **Different tool access** - A debugging agent with read-only permissions while main agent can write
- **Specialized execution** - Complex, self-contained tasks that benefit from focused instructions
- **Examples**: code reviewer, test suite runner, documentation generator, commit message writer

**Use Skills when you need:**
- **Domain knowledge in current context** - Teaching Claude your coding standards as you work
- **Workflow guidance** - TDD discipline, git workflows, architectural patterns
- **Shared standards** - Company-wide conventions that every task should follow, distributed across team or enterprise
- **Examples**: test-driven-development, API design patterns, error handling conventions

**Rule of thumb**: If the task needs to "forget" what you've been doing, use a subagent. If it needs to "remember and apply new rules", use a skill.

## Agents and Skills in Practice: Superpowers Plugin

A powerful real-world example is [Jesse Vincent](https://en.wikipedia.org/wiki/Jesse_Vincent)'s [Superpowers](https://blog.fsck.com/2025/10/09/superpowers/) plugin - a collection of skills and agents that enforce software engineering best practices. Rather than only relying on separate subagents for each phase of development, Superpowers uses skills to guide Claude through a disciplined workflow:

| Stage | Workflow Component | Type | Description |
|-------|-------------------|------|-------------|
| 1 | brainstorming | Skill | Refines rough ideas through questions, explores alternatives, presents design in sections for validation |
| 2 | using-git-worktrees | Skill | Creates isolated workspace on new branch, runs project setup, verifies clean test baseline |
| 3 | writing-plans | Skill | Breaks work into bite-sized tasks (2-5 minutes each) with exact file paths, complete code, verification steps |
| 4 | subagent-driven-development | Agent | Dispatches fresh subagent per task with two-stage review (spec compliance, then code quality) |
| 5 | test-driven-development | Skill | Enforces RED-GREEN-REFACTOR cycle: write failing test, watch it fail, write minimal code, watch it pass, commit |
| 6 | requesting-code-review | Agent | Reviews work against plan, reports issues by severity; critical issues block progress |
| 7 | finishing-a-development-branch | Skill | Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree |

At the time of writing, the only agent in the repository is a code-review agent.

The Superpower plugin demonstrates how skills and agents are utilized together.


### Installing Superpowers

You can install via [Claude's plugin system](https://docs.claude.com/en/docs/claude-code/plugins). You'll need Claude Code 2.0.13 or newer:

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

After installation, restart Claude Code to make them active. If you want to remove it:

```bash
/plugin remove superpowers@superpowers-marketplace
```

Superpowers is designed to be a community-driven effort. I'm excited to see how it will grow!

## Practical Decision-Making: Real Scenarios

The Claude Code community has created hundreds of production-ready subagents. Here are real-world scenarios using subagents from popular repositories like [wshobson/agents](https://github.com/wshobson/agents) (22.8k stars) and [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents).

**Scenario 1: You need to review code quality and security**
- **Use**: Subagent (`code-reviewer` from wshobson/agents)
- **Why**: Code review should evaluate your work in isolation, without being influenced by your implementation context. The reviewer integrates with tools like SonarQube, CodeQL, and Semgrep for comprehensive analysis.

**Scenario 2: You want to enforce test-driven development**
- **Use**: Skill (like Superpowers' `test-driven-development`)
- **Why**: TDD discipline needs to stay within your current context so tests inform the code you're actively writing. The skill guides your workflow step-by-step.

**Scenario 3: You're debugging an unexpected error**
- **Use**: Subagent (`debugger` from wshobson/agents)
- **Why**: Debugging benefits from isolated context focused solely on the error, systematic investigation, and potentially read-only permissions to prevent accidental changes during investigation.

**Scenario 4: You need to optimize database performance**
- **Use**: Subagent (`db-optimizer` from VoltAgent collection)
- **Why**: Database optimization is a specialized, self-contained task requiring deep expertise in query analysis, indexing, and performance tuning—separate from your main development context.

**Scenario 5: You want all API endpoints to follow OpenAPI 3.0 standards**
- **Use**: Skill (`api-design-standards`)
- **Why**: Design standards should guide you as you build, shared across the team, applied consistently to every endpoint you create.

**Scenario 6: You need to respond to a production incident**
- **Use**: Subagent (`incident-commander` or `devops-firefighter` from VoltAgent collection)
- **Why**: Incident response requires isolated, focused context with emergency procedures and restricted permissions to prevent escalation during high-pressure situations.

## Further Reading
Other excellent posts on how they use Claude Code: https://blog.sshh.io/p/how-i-use-every-claude-code-feature
- https://www.siddharthbharath.com/claude-code-the-complete-guide/

## References

[0]:[How Claude Code Works - Jared Zoneraich, PromptLayer](https://www.youtube.com/watch?v=RFKCzGlAU6Q) 
[1]:[Buidling Agents with the Claude Agent SDK - Anthropic](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
[2]:[Official claude code docs](https://code.claude.com/docs/en/memory.md)
[3]:[Claude Code Guide](https://github.com/Cranot/claude-code-guide)
