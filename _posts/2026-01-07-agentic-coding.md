---
layout: post
title:  Agentic Code Development with Claude Code
categories: [AI Coding, LLMs, Claude Code]
---

Early users treated LLMs as one-shot text generators. Users focused on clever wording, examples, and formatting of their prompts to achieve their goals. This became known as "prompt engineering". Prompt Engineering worked for simple tasks, but broke down as soon as people needed memory, tools, retrieval, or multi-step reasoning.

As systems became stateful, tool-using, and long-running, it became clear that model behavior was driven less by phrasing and more by what information was present, structured, ordered, and refreshed over time. The problem shifted from “How do I word this prompt?” to “What context should the model see at this moment, and why?”

That shift—managing instructions, state, memory, retrieved knowledge, and tool outputs across interactions—is what became known as context engineering.

Claude Code runs an agentic loop [[1]][[2]]: you submit a prompt → Claude chooses tools → executes them → responds. Within this loop, Claude can invoke two context management tools: **subagents** [[3]] (isolated AI instances with specialized instructions) or **skills** [[3]] (prompt templates that enhance the current conversation). Claude will automatically invoke the appropriate agent or skill available. However, having the right agents and skills for your work is key to skillful agentic development. This post goes into the main principles of these tools, and practical tips on getting started with them.

**TL;DR**:
- **Subagents** = Fresh start, isolated context, specialized tools (use for code review, testing, debugging)
- **Skills** = Enhanced current context, shared knowledge (use for standards, workflows, TDD)
- Codify new patterns, standards, or workflows as a new Subagent or Skill for repeatability
- Appropriate use of Skills and Subagents helps with context engineering, enhancing your workflow, making sure Claude Code will always follow your prompts and your processes.

## Subagents
Subagents receive a tightly scoped slice of context to perform a specific task (e.g., search, refactor, test, or analyze) independent from the main conversation context. Their outputs are then merged back into the main agent’s context, allowing complex coding workflows to scale without overwhelming a single prompt or context window.

Claude Code parses the user's prompt to infer intent, then calls the appropriate subagent as it would other tools. Each time a subagent is triggered, it:
1. Starts with a blank context window
2. Loads the project's `CLAUDE.md` file
3. Loads its own set of focused instructions
4. Receives specific context from the main agent

Based on this workflow, a cluttered `CLAUDE.md` risks degrading the performance of your subagents. For this reason, `CLAUDE.md` should be kept lean (there are [other reasons](https://x.com/Arindam_1729/status/2013273760619794778) to keep `CLAUDE.md` lean too. e.g, Claude may not follow your instructions or invoke skills because your `CLAUDE.md` file is too verbose). With subagents, you can split up a large, cluttered `CLAUDE.md` into specific instructions for specific agents - planning, reviewing, styling, committing, etc. You could build your own agents, but I recommend starting with pre-built ones that have already been battle tested [[4]]. Claude Code already comes with pre-defined agents -- for example, the `plan` mode uses a Plan subagent.

### Under the Hood
Subagents are defined as markdown files that live in `.claude/agents/`. Like general AI agents, they have access to specific instructions and tools.

A simple subagent could look like:
```md
---
name: your-sub-agent-name
description: A CONCISE description of when this subagent should be invoked
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
(from the official docs [[5]])

During session start, Claude Code scans for available subagents. Then, during evaluation, Claude Code proactively delegates tasks to subagents based on:
* The task description in your request
* The description field in subagent configurations
* Current context and available tools
When this happens, the main agent will pass relevant context to the subagents

You can also explicitly invoke an agent by mentioning it in your command:
```
> ask the debugger subagent to investigate this error
```

### Things to Consider: The Handoff Issue
When you invoke a subagent, the main agent passes only a summary of what it thinks the subagent needs—the subagent starts fresh with your `CLAUDE.md` file, its own instructions, and whatever context the main agent provides. This creates an information gap: nuanced decisions, discovered patterns, and architectural discussions from your conversation may get lost. If the main agents don't give subagents sufficient context, then the subagents will operate blindly and essentially "hallucinate".

Given this issue, agents are most suitable for tasks like:
* Self-contained tasks: code review, testing, documentation—fresh eyes without implementation bias
* Specialized analysis: security audits, performance profiling benefit from isolated evaluation
* Greenfield projects with minimal accumulated context
* Tasks with clear boundaries that provide sufficient context in the request itself

And you should avoid using agents for tasks like:
* Complex brownfield projects with deep architectural context spread across many files [[6]]
* Large refactoring requiring understanding of intricate component relationships
* Tasks heavily dependent on conversation history built with the main agent
* When tasks are derived from nuanced design decisions that only exist in the conversation context

These types of context-sensitive tasks are more suitable to be handled via Skills.

**Key takeaway**: Subagents excel at isolated, self-contained tasks where fresh context prevents bias. Use them when you need specialized analysis without influence from your work-in-progress.

## Agent Skills
Rather than invoking subagents to carry out specific tasks, Anthropic introduced agent Skills to conditionally inject additional context to the current conversation based on your instructions.

Skills are specialized prompt templates that inject domain-specific instructions into the conversation context. When a Skill is invoked, it modifies both the conversation context (by injecting instruction prompts) and the execution context (by changing tool permissions and potentially switching the model). Instead of executing actions directly, skills expand into detailed prompts that prepare Claude to solve a specific type of problem. Each skill appears as a dynamic addition to the tool schema that Claude sees [[7]].

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

What this means: with code template and scripts to run, we can give agents ways to access our environment - bash shell, our machine, ways to access .docx and .csv files, etc. We let agents write code on the fly to interact with these new file formats. This increases the capabilities of what the agents are able to achieve.

Skills are the next evolution from model context protocols (MCPs) -- Skills tell Claude how to use tools; MCP provides the tools. For example, an MCP server connects Claude to your database, while a Skill teaches Claude your data model and query patterns.

For more details, see the official skills documentation [[8]].

#### Caveat - Too Many Agents and Skills
Careful not to install too many agents and skills with similar directives -- you want to make sure Claude is always choosing the one optimal agent or skill for each task! Check which agents and skills you have installed with `/agents` and `/skills` in the Claude CLI.

Similarly, do not allow your agents and skills to access more tools than it needs. Your agent is more likely to select the wrong action or take an inefficient path, dumbing it down.

#### Caveat - Additional Token Consumption
Because Skills usually involve prompt injection with instructions for complex operations, they typically consume more tokens than if you had just typed something simple into the dialog window (e.g., `format my citations in xyz format`). However, this extra cost is often worth it because the Skills will ensure output specificity.

**Key takeaway**: Skills add domain knowledge to your current context—use them for workflows, standards, and patterns that should guide your work continuously rather than being evaluated in isolation.

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

**Rule of thumb**: If you want the task to start fresh without prior context, use a subagent. If it needs to "remember and apply new rules", use a skill.

## Geting started: Agent and Skill repositories

### Claude Code Plugin Marketplace (Recommended)

The easiest way to install pre-built subagents is through Claude Code's plugin system:

```bash
/plugins  # In Claude Code CLI - browse and install plugins
```

To remove a plugin, do
```bash
/plugin remove
```

### Popular Community Collections

#### obra/superpowers ([Github](https://github.com/obra/superpowers))
A collection of Skills that have been thoroughly battle tested by Jesse Vincent [[9]]. Great for ensuring good software engineering workflows.

```bash
# Claude CLI
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**Real-world workflow example:**

Superpowers [[10]] uses skills to guide Claude through a disciplined development workflow:

| Stage | Workflow Component | Type | Description |
|-------|-------------------|------|-------------|
| 1 | brainstorming | Skill | Refines rough ideas through questions, explores alternatives, presents design in sections for validation |
| 2 | using-git-worktrees | Skill | Creates isolated workspace on new branch, runs project setup, verifies clean test baseline |
| 3 | writing-plans | Skill | Breaks work into bite-sized tasks (2-5 minutes each) with exact file paths, complete code, verification steps |
| 4 | subagent-driven-development | Agent | Dispatches fresh subagent per task with two-stage review (spec compliance, then code quality) |
| 5 | test-driven-development | Skill | Enforces RED-GREEN-REFACTOR cycle: write failing test, watch it fail, write minimal code, watch it pass, commit |
| 6 | requesting-code-review | Agent | Reviews work against plan, reports issues by severity; critical issues block progress |
| 7 | finishing-a-development-branch | Skill | Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree |

**Key insight**: Notice the pattern—Skills dominate (5/7 stages) because most development requires continuous context. Subagents appear only where isolation adds value: executing independent tasks and providing unbiased code review.

**Example scenarios:**
- **Enforce test-driven development**: Use the `test-driven-development` skill to keep TDD discipline within your current context so tests inform the code you're actively writing
- **Follow API design standards**: Skills like `api-design-standards` guide you as you build, applied consistently to every endpoint you create

Superpowers is designed to be a community-driven marketplace of Agents and Skills. Exciting to see how it will grow!

#### wshobson/agents ([GitHub](https://github.com/wshobson/agents))

A comprehensive production-ready system combining 99 specialized AI agents, 15 multi-agent workflow orchestrators, and 107 agent skills organized into 67 focused plugins. The repository is consistently cited in community resources as one of the top subagent collections.

```bash
# Claude CLI
/plugin marketplace add wshobson/agents-marketplace
/plugin install agents@wshobson
```

**Example scenarios:**
- **Code review**: Use the `code-reviewer` subagent to evaluate your work in isolation, without being influenced by your implementation context. The reviewer integrates with tools like SonarQube, CodeQL, and Semgrep for comprehensive analysis.
- **Debugging**: Use the `debugger` subagent for isolated context focused solely on the error, with systematic investigation and potentially read-only permissions to prevent accidental changes during investigation.

#### VoltAgent/awesome-claude-code-subagents ([GitHub](https://github.com/VoltAgent/awesome-claude-code-subagents))

The most comprehensive reference repository for Claude Code subagents, featuring 100+ specialized AI agents for full-stack development, DevOps, data science, and business operations. "The most powerful Claude agents feel like hiring a team of experts—but you get code reviews, migrations, and tests done in minutes" [[11]]; "Performs comprehensive code reviews with the thoroughness of a senior engineer" - developers report catching subtle race conditions that would have caused production failures [[12]].

Browse: https://github.com/VoltAgent/awesome-claude-code-subagents

**Example scenarios:**
- **Database optimization**: Use the `db-optimizer` subagent for specialized, self-contained tasks requiring deep expertise in query analysis, indexing, and performance tuning—separate from your main development context.
- **Incident response**: Use the `incident-commander` or `devops-firefighter` subagent for isolated, focused context with emergency procedures and restricted permissions to prevent escalation during high-pressure situations.

### Manual Installation (Alternative)

If an agent isn't available as a plugin:

1. Download the `.md` file from the repository
2. Copy to `.claude/agents/` in your project root
3. Restart Claude Code to detect the new agent
4. Test: `ask the [agent-name] to...`

## Building Your Own Agents or Skills
If your pattern or standard isn't found in an existing skill, you can codify it as a new skill. Based on community recommendations [[6]]:
- **Start simple**: Generate initial subagents with Claude, then iterate to customize for your specific needs. Ask `I want to do XYZ, is this task better handled as a Skill or by a subagent?`
- **Design focused subagents**: Single, clear responsibilities work better than trying to make one subagent do everything
- **Create reproducible pipelines**: Use roles like Product Spec → Architect → Implementer/Tester for repeatable workflows
- **Test and iterate**: Your skill or agent may not work as expected at first. Keep testing and iterating as edge cases appear.

If you do create you own skills, I encourage you to read more about skills in [Claude Agent Skills: A First Principles Deep Dive [7]](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/#:~:text=Claude%20Agent%20Skills%20Overview,on%20the%20skill%20descriptions%20provided). Particularly useful are the common patterns you'll find:
* Script Automation - Complex operations requiring multiple commands or deterministic logic
* Read - Process - Write: Fille transformation and data processing
* Search - Analyze - Report: For code analysis
* Command Chain Execution: Multi-step operations with dependencies for CI/CD-like workflows.
* Multi-step workflows that require user input
* Template-based generation
* Iterative refindment
* Context aggregation - combining information from ultiple sources

## Key Takeaways

To master agentic development with Claude Code:

1. **Understand the context distinction**: Subagents start fresh (isolation), Skills enhance current conversation (continuity)
2. **Apply the decision framework**: Need unbiased evaluation? → Subagent. Need ongoing guidance? → Skill.
3. **Start with existing tools**: Explore the plugin marketplace before building custom solutions
4. **Make your workflow repeatable**: Codify new patterns and standards as skills
5. **Follow single responsibility**: Each agent/skill should have one clear purpose
6. **Expect Skills to dominate**: Most workflows require continuous context—subagents are specialists, not generalists

The shift from prompt engineering to context engineering means thinking strategically about what information your agents need, when they need it, and whether that knowledge should persist or start fresh. Master this, and you'll build more reliable, maintainable agentic workflows.

## References

[1]: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk "Building Agents with the Claude Agent SDK - Anthropic"
[2]: https://www.youtube.com/watch?v=RFKCzGlAU6Q "How Claude Code Works - Jared Zoneraich, PromptLayer"
[3]: https://code.claude.com/docs/en/memory.md "Official Claude Code docs"
[4]: https://github.com/Cranot/claude-code-guide "Claude Code Guide"
[5]: https://code.claude.com/docs/en/sub-agents "Claude Code Sub-agents Documentation"
[6]: https://www.eesel.ai/blog/subagents-in-claude-code "Subagents in Claude Code - eesel.ai"
[7]: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/ "Claude Skills Deep Dive - Lee Han Chung"
[8]: https://code.claude.com/docs/en/skills "Claude Code Skills Documentation"
[9]: https://en.wikipedia.org/wiki/Jesse_Vincent "Jesse Vincent - Wikipedia"
[10]: https://blog.fsck.com/2025/10/09/superpowers/ "Superpowers - Jesse Vincent's blog"
[11]: https://dev.to/voltagent/100-claude-code-subagent-collection-1eb0 "100+ Claude Code Subagent Collection - VoltAgent"
[12]: https://dev.to/necatiozmen/10-claude-code-subagents-every-developer-needs-in-2025-2ho "10 Claude Code Subagents Every Developer Needs in 2025 - Necati Özmen"

1. [Building Agents with the Claude Agent SDK - Anthropic](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
2. [How Claude Code Works - Jared Zoneraich, PromptLayer](https://www.youtube.com/watch?v=RFKCzGlAU6Q)
3. [Official Claude Code docs](https://code.claude.com/docs/en/memory.md)
4. [Claude Code Guide](https://github.com/Cranot/claude-code-guide)
5. [Claude Code Sub-agents Documentation](https://code.claude.com/docs/en/sub-agents)
6. [Subagents in Claude Code - eesel.ai](https://www.eesel.ai/blog/subagents-in-claude-code)
7. [Claude Skills Deep Dive - Lee Han Chung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
8. [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
9. [Jesse Vincent - Wikipedia](https://en.wikipedia.org/wiki/Jesse_Vincent)
10. [Superpowers - Jesse Vincent's blog](https://blog.fsck.com/2025/10/09/superpowers/)
11. [100+ Claude Code Subagent Collection - VoltAgent](https://dev.to/voltagent/100-claude-code-subagent-collection-1eb0)
12. [10 Claude Code Subagents Every Developer Needs in 2025 - Necati Özmen](https://dev.to/necatiozmen/10-claude-code-subagents-every-developer-needs-in-2025-2ho)

## Further Reading

- [Best Practices for Agentic Coding - Anthropic](https://code.claude.com/docs/en/best-practices)
- [Effective Context Engineering for AI Agents - Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Context Engineering Guide - Prompting Guide](https://www.promptingguide.ai/guides/context-engineering-guide)
- [Context Engineering - DataCamp](https://www.datacamp.com/blog/context-engineering)
- [Context Engineering for Agents - LangChain](https://blog.langchain.com/context-engineering-for-agents/)
- [Context Engineering: What It Is and Techniques to Consider - LlamaIndex](https://www.llamaindex.ai/blog/context-engineering-what-it-is-and-techniques-to-consider)
- [Context Engineering Best Practices - Redis](https://redis.io/blog/context-engineering-best-practices-for-an-emerging-discipline/)
- [Vibe Coding: Context Engineering in 2025 Software Development - Thoughtworks](https://www.thoughtworks.com/insights/blog/machine-learning-and-ai/vibe-coding-context-engineering-2025-software-development)
- [Context Engineering - Flowhunt](https://www.flowhunt.io/blog/context-engineering/)
- [Context Engineering for AI Agents - Kubiya](https://www.kubiya.ai/blog/context-engineering-ai-agents)
- [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
