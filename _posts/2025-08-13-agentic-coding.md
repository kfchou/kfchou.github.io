---
layout: post
title:  Agentic Code Development with Claude Code
categories: [AI Coding, LLMs, LLM Toolchain]
---

Any expeienced dev who tried coding tools like Cursor, Windsurf, or Claude Code knows: vibe coding is great for one-off scripts. As projects become large, vibe-coding creates complex slop. The code works, but is generally problematic, not maintainable, potentially vulnerable and generally unsuitable for production environments. The good news for devs is in order to overcome this, agentic AI systems must have humans in the loop - particularly experienced humans who are able to guide the agent in the right direction, acting as PM and architect. This blog is a guide for that experienced human to write quality, production level code using Claude Code.


## Under the hood: The Agentic Loop
The primary breakthrough for Claude Code came when its dev team realized they needed to "get out of the way" - remove complex prompts and scaffolds, and optimize the LLM for tool-use instead [0]. Tools can create deterministic outputs, solving the hallucination issue. Under the hood, Claude is a ReAct agent [1]:

![Anthropic Agent SDK event loop](image-2.png)

Let's look at this loop in more detail [2,3]:

```
Session Start:
  1. Load CLAUDE.md from all levels (enterprise, project, user)
  2. Load .claude/rules/ files (with glob pattern matching)
  3. Run SessionStart hook (if configured)
  4. Assemble system prompt with all context

Per User Input:
  1. User submits → UserPromptSubmit hook fires
  2. Claude decides what to do (may use multiple tools)
    - Each tool: PreToolUse → Tool runs → PostToolUse
  3. Claude responds
  4. Stop hook decides whether to continue
```

Given the detail above, let's consider:
* What should we put in CLAUDE.md?
* What tools are available to us?

## CLAUDE.md
To state the obvious, controlling context is the most important thing we need to do as we work with Claude Code. We need to keep each task focused, and avoid introducing unnecessary instructions.

Six month ago, the convention is to keep adding details to `CLAUDE.md`. Need Claude to always test your code? Add the instruction to `CLAUDE.md`. Want Claude to write commit messages in a certain way? Add it to `Claude.md`. As the file grows, the context gets cluttered. This way of working is the opposite of good context management; if we're researching the codebase about a particular feature, we don't need Claude to know how to write commit messages and write tests.

We should instead keep `CLAUDE.md` as lean as we can. Some tips:
* Do not `@` files. Instead, mention file paths and when those files should be read.
* If you say "Never do xyz", you must also say "Instead, do abc"
* Do not write a manual for specific tasks - delegate these to subagents (see below).

For complex tasks, you might say
```
For <complex usage> or <error> see path/to/<tool>_docs.md
```
... even better, let us delegate this task to a spcific subagent!

## Subagents
Subagents are agentic tools Claude Code can call within the agentic loop. They are simply markdown files that live in `.claude/agents/`. Like general AI agents, they have access to specific instructions and tools. For example, the plan mode uses a Plan subagent.

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

Claude will scan for available subagents at session start. During evaluation, **Claude Code proactively delegates tasks to subagents** based on:
* The task description in your request
* The description field in subagent configurations
* Current context and available tools
When this happens, the main agent will pass relevant context to the subagents

You can also explicitly invoke an agent by mentioning it in your command:
```
> ask the debugger subagent to investigate this error
```

### Under the Hood
Each time a subagent is triggered, it:
1. Loads the project's `CLAUDE.md` file
2. Loads its own set of focused instructions
3. The main agent gives a set of prompts to the subagent

If you clutter your `CLAUDE.md`, you risk degrading the performance of your subagents as well -- another reason to keep this file lean. With subagents, you can split up your giant `CLAUDE.md` into specific instructions for specific agents - planning, reviewing, styling, committing, etc. You could build your own agents, but I recommend starting with pre-built ones that have already been battle tested (see PLACEHOLDER).

### Pre-Configured agents
There are github [repositories](https://github.com/VoltAgent/awesome-claude-code-subagents) keeping track of a large collection of pre-configured agents. Agents can also be [installed as plugins](https://github.com/wshobson/agents). To explore plugins, type `/plugins` in the Claude Code CLI.


### The Handoff Issue
The fact that new subagents spawn with a fresh context presents some drawbacks. If the main agents don't give subagents sufficient context, then the subagents will operate blindly and essentially "hallucinate". "This is a particular nightmare in existing, complex codebases ("brownfield" projects) and is a big reason why subagents seem to work best on brand-new projects or very self-contained tasks." [https://www.eesel.ai/blog/subagents-in-claude-code]. One way to overcome this issue is to come to an agreement of what the hand-off context will be, but it is cumbersome to do this every time. As of the time of this writing, there's no good solution to this issue.

An alternative to specialist subagents is using Claude's build in Task(...) feature to spawn clones of the general agent, as described by Shrivu Shankar:

> I put all my key context in the CLAUDE.md. Then, I let the main agent decide when and how to delegate work to copies of itself. This gives me all the context-saving benefits of subagents without the drawbacks. The agent manages its own orchestration dynamically.


### Decreased Speed, Increased Cost
Everytime you call a subagent, it needs to build its understanding of the task from scratch, and that burns time and processing power. And becaue each subagent has its own context, running multiple agents can burn through tokens quickly. They may increase quality but it may end up being more costly; you get what you pay for.


## Agent Skills
Rather than invoking subagents to carry out specific tasks, Anthropic introduced agent "skills" to conditionally inject additional context to the current conversation based on your instructions.

Skills are specialized prompt templates that inject domain-specific instructions into the conversation context. When a skill is invoked, it modifies both the conversation context (by injecting instruction prompts) and the execution context (by changing tool permissions and potentially switching the model). Instead of executing actions directly, skills expand into detailed prompts that prepare Claude to solve a specific type of problem. Each skill appears as a dynamic addition to the tool schema that Claude sees [https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/#:~:text=Claude%20Agent%20Skills%20Overview,on%20the%20skill%20descriptions%20provided.]

### Under the hood
Agent skills are simply folders that contain templates for subagents. Within the folder, you can have:
* Markdown files with specific instructions (similar to the agent markdown files)
* Code templates
* Scripts to run

What this means: with code template and scripts to run, we give agents more ways to access our environment - bash shell, our machine, .docx and .csv files, etc. We let agents write code on the fly to interact with these new file formats. This will increase the capabilities of what the agents are able to achieve.

**Skills vs. subagents**: Skills can be shared across the team or enterprise. Skills add knowledge to the current conversation. Subagents run in a separate context with their own tools. Use Skills for guidance and standards; use subagents when you need isolation or different tool access.

**Skills vs. MCP**: Skills tell Claude how to use tools; MCP provides the tools. For example, an MCP server connects Claude to your database, while a Skill teaches Claude your data model and query patterns.

https://code.claude.com/docs/en/skills


### Claude, a Senior Engineer?
Now, this is where things gets interesting. [Jesse Vincent](https://en.wikipedia.org/wiki/Jesse_Vincent) recently created a set of Skills that gives Claude Superpowers (or so he [claims](https://blog.fsck.com/2025/10/09/superpowers/) - though I'm tempted to believe him based on his credentials). Essentually, the skills enforce the following ways of working:

Stage	Skill	Trigger
1	brainstorming	Before writing any code
2	using-git-worktrees	After design approval
3	writing-plans	With approved design
4	subagent-driven-development	With plan ready
5	test-driven-development	During implementation
6	requesting-code-review	Between tasks
7	finishing-a-development-branch	When tasks complete

This makes software development systematic and enforces best practices.

You can install them via [Claude's plugin system](https://docs.claude.com/en/docs/claude-code/plugins). 

You'll need Claude Code 2.0.13 or newer: 
```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace 
```

After installation, restart Claude Code to make them active. If you hate it, you can remove it with
```
/plugin remove superpowers@superpowers-marketplace 
```

Superpower designed to be a community-driven effort. I'm excited to see how it will grow!

### What happened with Spec-Driven Development (SDD)?
For a while around mid-2025, SDD emerged as the solution against the slop generated by vibe-coding. The idea is simple - spend a lot of effort up front writing the specs, break tasks down into small, digestable pieces, and have the coding agent follow it closely. But just like in actual software development, specs often get bloated, become difficult to review, and a lot of time can get wasted on getting the spec right. On the other hand, it's often more efficient if engineers can identify a generally correct direction, start building, and iterate. With SDD, spec creation, review, iteration, and governance introduces extra cycles early in the project, and often hinders more than helps. This is my personal experience.

Although these issues exist, as of December 2025, it seems like there is still a generally positive sentiment on reddit [https://www.reddit.com/r/ChatGPTCoding/comments/1otf3xc/does_anyone_use_specdriven_development/] aroud SDD and tools like spec-kit. Whether to use SDD seems entirely context dependent.

## Further Reading
Other excellent posts on how they use Claude Code: https://blog.sshh.io/p/how-i-use-every-claude-code-feature
- https://www.siddharthbharath.com/claude-code-the-complete-guide/

## References

[0]:[How Claude Code Works - Jared Zoneraich, PromptLayer](https://www.youtube.com/watch?v=RFKCzGlAU6Q) 
[1]:[Buidling Agents with the Claude Agent SDK - Anthropic](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
[2]:[Official claude code docs](https://code.claude.com/docs/en/memory.md)
[3]:[Claude Code Guide](https://github.com/Cranot/claude-code-guide)





# Appendix
## Other random tips
### Context management within a session
* Avoid compaction. By the time your coding agent have done enough work to require compaction, you likely already experience [context rot](https://research.trychroma.com/context-rot) - even though models like Opus can handle 1MM tokens, its performance likely have already degraded severely. Better to keep context tight to help keep Claude focused. Even after compaction, you risk introducing sementic shift.
* After planning, if Claude proposes a large piece of work, tell Claude to "make the plan multi-phased"
* Use Github issues to keep track of different phases of the plan. 
* Claude code works well with the Github CLI tool to help you manage and track issues, PRs, and the like.
* Ask Claude to review your context usage and suggest optimizations.
* Claude has a built-in thinking budget based on these keywords:
  * "think": 4,000 tokens
  * "megathink": 10,000 tokens
  * "ultrathink": maximum budget

### Do meta-analysis on the codebase
It's important to emphasize human development and maintainability in your specs.

Claude may implement features that work, but not always in a way that makes sense. When it refactors code, it may unnecessarily create new variables and deprecate others. This is bad for many reasons:
* Bloat &rarr; increased context &rarr; consuming unnecessary tokens &rarr; increased cost
* Confusing for human readers &rarr; decreased maintainability &rarr; time wasted

Ask Claude to do meta-analysis on the code base to find possible bloat and oppotunities to simplify the code logic, increase performance, and harmonize duplicated functionalities. Do this every now and then to ensure bloat is kept to a minimum.

Sometimes it's easier to visualize the codebase as a mermaid diagram. Ask Claude to give you code to a mermaid diagram describing the codebase as you plan or review.

Memory files?
If working on multiple projects, you can keep "memory" files in your machine's home directory `~/.claude/CLAUDE.md`. You can jump to these with the `/memory` command

Claude may hard-code a lot of values. This is bad practice for obvious reasons. In your specs, Tell Claude what to use as a source of truth. **Key terms like "dynamic" and "configurability"** will help avoid hard-coded values and increase maintainability.

### The most important commands to know
* `/compact` -- summarize your chat history
* `/clear` -- clears your chat history
* `/resume` -- resume a previous conversation.
* `/install-git-app`
* `/context` <-------------- available as of version 1.0.86. Helps keep track of context window. It's important to keep track of your context periodically. [Ref](https://claudelog.com/mechanics/context-inspection/).

### Custom commands (accesss with `/`)
Create a markdown file: `.claude/commands/<command-name>.md`

The file would look something like this

```
<description of the command>

$ARGUMENTS (only use this line if you want users to pass arguments to the command)

<detailed instructions for claude>
```

### Actually useful MCP servers

Have a browser UI? Use Playwright:
```
    claude mcp add playwright npx @playwright/mcp@latest
```

### Multiple Claudes
Use `git worktree` to open multiple Claude instances and have them all work in parallel
1. Make a folder `.trees`
2. Make worktrees with `git worktree add`:
   * `git worktree add .trees/feature_1`
   * `git worktree add .trees/feature_2`
   * `git worktree add .trees/feature_3`
3. Open up a terminal for each worktree directory. Right click on the directory and select "Open in integrated terminal".
4. Open Claude in each terminal and let them cook.
5. After all the parallel work is finished, tell Claude to merge in all of the worktrees in the `.trees` folder and fix any conflicits if there are any.

Anecdotally, doing parallel work like this only makes sense if each piece of work is self-contained and limited in scope.