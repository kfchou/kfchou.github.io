---
layout: post
title:  Claude Code Best Practices
categories: [AI Coding, LLMs, LLM Toolchain]
---

I recently build a browser-based javascript game. I have very little JS experience and have learned a lot along the way, both in terms of JS and working with Claude. These are my takeaways.

# Best Practices
## Use Spec-Driven development
`CLAUDE.md` is added to the context in every conversation with claude you have. You can have Claude analyze your code and create a `CLAUDE.md` file for you with `/init`. Or you can make one yourself. Customize this file with your instructions. Things that should go into `CLAUDE.md` are like programming principles (e.g., SOLID or DRY), langauges and frameworks you want it to use, instructions for testing and running the code, and general "How to work" or "How to approach my instructions" type of information. This is similar to `.cursor.md` if you're used to that.

I also recommend adding a `PRD.md` or `features.md` file to keep track of features in the project. Tell claude to reference these files as it work and check it off as each feature is verified completed. Each item should have a brief description of the feature along with the files and lines where these features are implemented. These files serve as a kind of "memory" for Claude; they help Claude find relevant context sooner and reduce the amount of tokens used in searching for the relevant context.

Claude may hard-code a lot of values. This is bad practice for obvious reasons. In your specs, Tell Claude what to use as a source of truth. Key terms like "dynamic" and "configurability" will help avoid hard-coded values and increase maintainability.

Speaking of which...

## Do meta-analysis on the codebase
It's important to emphasize human development and maintainability in your specs.

Claude may implement features that work, but not always in a way that makes sense. When it refactors code, it may unnecessarily create new variables and deprecate others. This is bad for many reasons:
* Bloat &rarr; increased context &rarr; consuming unnecessary tokens &rarr; increased cost
* Confusing for human readers &rarr; decreased maintainability &rarr; time wasted

Ask Claude to do meta-analysis on the code base to find possible bloat and oppotunities to simplify the code logic, increase performance, and harmonize duplicated functionalities. Do this every now and then to ensure bloat is kept to a minimum.

## Manage Claude's context
Giving claude the right context is key to optimizing performance and minimizing cost.

If you're on Claude Pro (the $20/month plan), you're likely to hit your maximum usage limit every 2-3 hours, then you're forced to wait a few more hours for your quota to be re-set. Minimizing your token usage will help you work more efficiencly and reduce costs down the road.

What context is claude using? Use `/context` to find out!

So how do you give the right context?
* Write good specs
* Use Planning mode frequently to preview the proposed changes
* Ask Claude to review your context usage and suggest optimizations.
* Use Plan Mode combined with ultrathink for comprehensive analysis: **"Where is my context potentially inefficient and how can I optimize it?"**

### Ultrathink?
You can tell Claude to think more. This triggers more tokens to be used, but the additional analysis may be worth it if you're working on a complex problem.

Claude has a built-in thinking budget based on these keywords:
* "think": 4,000 tokens
* "megathink": 10,000 tokens
* "ultrathink": maximum budget


# Pro-tips
## Interacting with Claude
* Reference a file with `@`
* Toggle planning mode with shift + tab
* Access commands with `/`

## The most important commands to know
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

## Use claude to do your git commits
Having claude write your commit messages for you can make your work history more detailed and readable.


## Use MCP servers

Have a browser UI? Use Playwright:
```
    claude mcp add playwright npx @playwright/mcp@latest
```

## Multiple Claudes
Open multiple Claude instances and have them all work in parallel
1. Make a folder `.trees`
2. Make worktrees with `git worktree add`:
   * `git worktree add .trees/feature_1`
   * `git worktree add .trees/feature_2`
   * `git worktree add .trees/feature_3`
3. Open up a terminal for each worktree directory. Right click on the directory and select "Open in integrated terminal".
4. Open Claude in each terminal and let them cook.
5. After all the parallel work is finished, tell Claude to merge in all of the worktrees in the `.trees` folder and fix any conflicits if there are any.

