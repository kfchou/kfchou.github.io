---
layout: post
title:  Initial Learnings for Effective Use of Claude Code
categories: [AI Coding]
pinned: false
---
I spent more than 40 hours to build a javascript-based game (which you can play [here]({% post_url 2025-08-28-tower-defense %})). I use Python day to day, and operating in a new language and framework in a new AI tool presented a steep learning curve. In this post, I share some learnings.


## CLAUDE.md
To state the obvious, controlling context is the most important thing we need to do as we work with Claude Code. We need to keep each task focused, and avoid introducing unnecessary instructions.

Six months ago, the convention is to keep adding details to `CLAUDE.md`. Need Claude to always test your code? Add the instruction to `CLAUDE.md`. Want Claude to write commit messages in a certain way? Add it to `CLAUDE.md`. As the file grows, the context gets cluttered. This way of working is the opposite of good context management; if we're researching the codebase about a particular feature, we don't need Claude to know how to write commit messages and write tests. So how to go about this?

Update: context management has become much easier with the introduction of Agents and Skills. Read more about them [here]({% post_url 2026-01-07-agentic-coding %}).

We should keep `CLAUDE.md` as lean as we can. Some tips:
* Do not `@` files. Instead, mention file paths and when those files should be read.
* If you say "Never do xyz", you must also say "Instead, do abc"
* Do not write a manual for specific tasks - delegate these to subagents.
* Include general principles that always apply - maintainabilitiy, readability, SOLID and DRY principles, etc.
* Claude may hard-code a lot of values. This is bad practice for obvious reasons. In your specs, Tell Claude what to use as a source of truth. **Key terms like "dynamic" and "configurability"** will help avoid hard-coded values and increase maintainability.


For complex tasks, you might say
```
For <complex usage> or <error> see path/to/<tool>_docs.md
```

## Manage context within a session
* Avoid compaction. By the time your coding agent have done enough work to require compaction, you likely already experience [context rot](https://research.trychroma.com/context-rot) - even though models like Opus can handle 1MM tokens, its performance likely have already degraded severely. Better to keep context tight to help keep Claude focused. Even after compaction, you risk introducing semantic shift.
* After planning, if Claude proposes a large piece of work, tell Claude to "make the plan multi-phased"
* Use Github issues to keep track of different phases of the plan. 
* Claude code works well with the Github CLI tool to help you manage and track issues, PRs, and the like.
* Ask Claude to review your context usage and suggest optimizations.
* Claude has a built-in thinking budget based on these keywords:
  * "think": 4,000 tokens
  * "megathink": 10,000 tokens
  * "ultrathink": maximum budget
* If working on multiple projects, you can keep "memory" files in your machine's home directory `~/.claude/CLAUDE.md`. You can jump to these with the `/memory` command

Update 2026-01-07: The thinking budget is now set to maximum by default in Claude Code, so triggering ultrathink is no longer necessary ([source](https://www.reddit.com/r/ClaudeCode/comments/1qe989p/thinking_modes_are_not_available_anymore_on/)).

## Do meta-analysis on the codebase
Claude may implement features that work, but not always in a way that makes sense. When it refactors code, it may unnecessarily create new variables and deprecate others. This is bad for many reasons:
* Bloat &rarr; increased context &rarr; consuming unnecessary tokens &rarr; increased cost
* Confusing for human readers &rarr; decreased maintainability &rarr; time wasted

**Reduce Bloat**: Ask Claude to do meta-analysis on the code base to find possible bloat and opportunities to simplify the code logic, increase performance, and harmonize duplicated functionalities. Do this every now and then to ensure bloat is kept to a minimum.

**Visualize the codebase**: Sometimes it's easier to visualize the codebase as a mermaid diagram. Ask Claude to give you code to a mermaid diagram describing the codebase as you plan or review.

As your codebase grows in size, the tips in this section will become increasingly impactful.


## The important commands to know
* `/compact` -- summarize your chat history
* `/clear` -- clears your chat history
* `/resume` -- resume a previous conversation.
* `/install-git-app`
* `/context` <-------------- available as of version 1.0.86. Helps keep track of context window. It's important to keep track of your context periodically. [Ref](https://claudelog.com/mechanics/context-inspection/).

## Custom commands (accesss with `/`)
Create a markdown file: `.claude/commands/<command-name>.md`

The file would look something like this

```
<description of the command>

$ARGUMENTS (only use this line if you want users to pass arguments to the command)

<detailed instructions for claude>
```

## Actually useful MCP servers

Have a browser UI? Use Playwright:
```
    claude mcp add playwright npx @playwright/mcp@latest
```

## Multiple Claudes
Anecdotally, doing parallel work makes sense if each piece of work is self-contained and limited in scope.

Use `git worktree` to open multiple Claude instances and have them all work in parallel
1. Make a folder `.trees`
2. Make worktrees with `git worktree add`:
   * `git worktree add .trees/feature_1`
   * `git worktree add .trees/feature_2`
   * `git worktree add .trees/feature_3`
3. Open up a terminal for each worktree directory. Right click on the directory and select "Open in integrated terminal".
4. Open Claude in each terminal and let them cook.
5. After all the parallel work is finished, tell Claude to merge in all of the worktrees in the `.trees` folder and fix any conflicits if there are any.


## A note on Spec-Driven Development (SDD)
For a while around mid-2025, SDD emerged as the solution against the slop generated by vibe-coding. The idea is simple - spend a lot of effort up front writing the specs, break tasks down into small, digestable pieces, and have the coding agent follow it closely. But just like in actual software development, specs often get bloated, become difficult to review, and a lot of time can get wasted on getting the spec right. On the other hand, it's often more efficient if engineers can identify a generally correct direction, start building, and iterate. With SDD, spec creation, review, iteration, and governance introduces extra cycles early in the project, and often hinders more than helps.

In my personal experience, SDD hinders, rather than helps. However, as of December 2025, it seems like there is still a generally positive sentiment on [reddit](https://www.reddit.com/r/ChatGPTCoding/comments/1otf3xc/does_anyone_use_specdriven_development/) around SDD and tools like spec-kit. Whether to use SDD seems entirely context dependent.

## Additional readings

Other excellent posts on how they use Claude Code:

- [How I Use Every Claude Code Feature](https://blog.sshh.io/p/how-i-use-every-claude-code-feature)
- [Claude Code: The Complete Guide](https://www.siddharthbharath.com/claude-code-the-complete-guide/)
