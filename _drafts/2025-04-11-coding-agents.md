---
layout: post
title:  tbd
categories: [agents, project management]
excerpt: tbd
---

Vibe coding has been a huge trend lately. New [vibe coding tools](https://topvibecoding.tools/) are released every week. Tech influencers and execs are making claims that SWEs will be obselete and most code will be AI coded in a year's time. To me, that's all BS. A look a Cursor's recent wave of complaints demonstrates why skilled human engineers will still be necessary in the future. Some notable ones in particular are its limited context window (with the [workaround](https://www.reddit.com/r/cursor/comments/1j56j7i/found_a_workaround_for_cursor_context_limit/) being zipping your entire repo and pushing it to Gemini-Pro), getting stuck in a debugging loop, and overwriting exisiting code. Good software and project management practices can help you mitigate a lot of issues associated with AI code generation, but that highlights the fact that a skilled developer will benefit tremendously from the vibe coding tools, while non-developers will hit a wall once their project exceeds a certain size. Not to mention they won't be able to debug any issues that pop up.

I've written a lot of posts about good software practices like using git correctly and code testing. In this post, I'll write about something less technical -- being a project manager, project management workflow, and tools to help you with those tasks. Coding agents have been described as junior engineers, and its quite accurate. They code well, but does not manage projects. On the other hand, if you can manage the projects and orchestrate the engineers, then you'll be able to quickly build large projects while mitigating a lot of the issues vibe coders run into.

# Vibe coding like a PM

Every project starts with a plan of what you want to build. This typically goes into a **project requirements document** (PRD). For vibe coding purposes, it typically describes:
* Project Overview
* Specific Goals
* Tech Stack
* Functional Requirements
* Non-Functional Requirements

The first three sections could go into a `rules` document, such as `.cursor/rules.txt` or `.github/copilot-instructions.md`, and the functional requirements would represent specific tasks to be accomplished by your agent; they go into a `tasks.md` file.

# Rules document
You can generate a rules and best practices document via AI by giving it the tech stack of your choosing. 

Additionally, provide workflow related rules to tell the AI _how_ to code. Considering including:
* Coding approaches - emphasizing simplicity and documentation
  * "Avoid repeating code; reuse existing functionality when possible."
  * "Keep files concise, under 200-300 lines; refactor as needed."
  * "After major components, write a brief summary in /docs/[component].md (e.g., login.md)."
  * Principles: "Follow SOLID principles (e.g., single responsibility, dependency inversion) where applicable."
  * Guardrails: "Never use mock data in dev or prod—restrict it to tests." 
  * Context Check: "Begin every response with a random emoji (e.g., 🐙) to confirm context retention."
  * Efficiency: "Optimize outputs to minimize token usage without sacrificing clarity."
* Tech Stack
  * "Backend in Python."
  * "Frontend in HTML and JavaScript."
  * "Store data in SQL databases, never JSON files."
  * "Write tests in Python."
  * "If I specify additional tools (e.g., Elasticsearch for search), include them here."
  * "Never alter the stack without my explicit approval."
* Workflow Preferences
  * Focus: "Modify only the code I specify; leave everything else untouched."
  * Steps: "Break large tasks into stages; pause after each for my approval."
  * Planning: "Before big changes, write a plan.md and await my confirmation."
  * Tracking: "Log completed work in progress.md and next steps in TODO.txt."
  * Testing: "Include comprehensive tests for major features; suggest edge case tests (e.g., invalid inputs)."
  * Context Management: "If context exceeds 100k tokens, summarize into context-summary.md and restart the session."
  *  Adaptability: "Adjust checkpoint frequency based on my feedback (more/less granularity)." 
* Communication Preferences
  * Summaries: "After each component, summarize what’s done."
  * Change Scale: "Classify changes as Small, Medium, or Large."
  * Clarification: "If my request is unclear, ask me before proceeding." 
  * Planning: "For Large changes, provide an implementation plan and wait for approval."
  * Tracking: "Always state what’s completed and what’s pending."
  * Emotional Cues: "If I indicate urgency (e.g., ‘This is critical—don’t mess up!’), prioritize care and precision."

Credit to [reddit](https://www.reddit.com/r/ChatGPTCoding/comments/1j5l4xw/vibe_coding_manual/).

# Tasks/Functional PRD document
Here's an example with PRD based on some functional requirements ([source](https://www.youtube.com/watch?v=dutyOc_cAEU)):
![alt text](image.png)

The more specific you are in this document, the better the agent will do.

# Break your project down into tasks

[TaskMaster AI](https://github.com/eyaltoledano/claude-task-master) - CLI Tool to help break down tasks into logical order, considering dependencies between tasks. It can break complex tasks into smaller subtasks. Better integration for Cursor and Windsurf

[Roo Code](https://github.com/RooVetGit/Roo-Code) - VSCode Extension 