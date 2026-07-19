---
layout: post
title: "Tips to build good Agent Skills by Matt Pocock"
categories: [AI Coding, LLMs, Claude Code, Agent Skill]
---

These are notes taken from a [talk](https://www.youtube.com/watch?v=UNzCG3lw6O0) by Matt Pocock, where he shares his philosophy in designing agent skills. Matt is the author of the popular agent skill repository [mattpocock/skills](https://github.com/mattpocock/skills)(154k stars).

## 1. Trigger
The keyword `disable-model-invocation` in the skill file header can prevent your skill from being invoked by models, making them user-invoked only by using the command syntax: `/my-skill`. This prevents the skill frontmatter from taking up unnecessary space in your context window.

Why would you want this? Intentional user-invocation removes the ambiguity of knowing when skills are correctly triggered. The popular obra/superpowers skill repository is frequently updated, but most of those updates concerns with tweaking the skill description to make sure they're invoked at the right times.

To avoid this ambiguity, Matt would rather put cognitive load on users and make his skills all **user-invoked**.

Triggering is a common issue in production when building skills for non-SWE end users.

## 2. Structure
Each skill file should have
1. (model invoked skills) A description - why a skill should be used
1. how a skill is used -- step-by-step procedures? Well-defined goals/Constraints?
2. supporting information/references - templates, definitions, etc

Each skill file should be as small as possible. Why?
* Fewer tokens
* More maintainable
* More readable

Think about the different action branches of the skill. Many skills only have a single branch, but some have many. If there are many branches, use pointers to point to references to keep the file small.

Additional tips: avoid overfitting, the _how_ should be scalable

## 3. Steering
**Failure mode: Agent doesn't do what I want**

Fix: Use "leading words".

Leading words are jargony terminologies that pack in a lot of meaning. Repeat these words in your skill file so your agent clearly knows your intent. For exmaple, agents tend to code layer by layer (all of database, all of etl, all of visualization, etc), and instead, we want them to do smaller chunk of work and seek feedback early. In this case, we can use "verticle slice" as the leading word. This is a well-known terminology in the software world. Repeating this in your skill file will help ensure your agent understands it needs to work on verticle slices, not horizontal ones.

**Failure mode: Agent does too little.**

Fix: Hide the end goal.

Example: In plan mode, the agent is instructed to do two things:
1. Ask clarifying questions
2. Build a plan

You've probably experienced planning agents don't ask enough clarifying questions, and proceeds to plan eagerly.

Let's split planning up into two steps
1. `/grill-with-docs` -> ask clarifying questions
2. `/to-prd` -> write the plan

This hides the end goal from the agents and avoids eager execution.

## 4. Pruning
Failure modes:
* Massive skill files -- keep skills under 500 lines
* Repeating yourself
* Sediment -- accumulation over time, maybe by multiple users.
* No-ops -- things inside the skill that actually doesn't influence the Agent's behavior

Tips:
* Use deletion tests to prune
* See [mattpocock/writing-great-skills](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md)

---

## Evaluate your skills

notes from https://www.youtube.com/watch?v=0vphxNt4wyk

The most critical questions we're tracking:
- Are skills invoked when intended?
- Are skills silent (when not intended to be invoked)?
- Are the outcomes as expected?

Most checks can be regex against extracted code -- extract text from markdown responses (cheap to run, no llm call)
Register checks in a dispatch registy mapping check IDs to functions

When regex is not enough, we can use LLM as a judge. BUT, use them selectively to control API costs. LLM as a judge is still non-deterministic and can be unreliable (https://arxiv.org/html/2510.27106v1), so use pure regex when you can.

### Example from Google Deepmind's eval workflow
* YAML configs define setup files, CLI checks, and LLM judge criteria
* Automatically spins up an isolated, clean workspace env for every test run
* Executes automated ablation benchmarks (with vs without skills) to measure exact Skill Life
* Requires proof of positive Skill Life before any skill PR gets merged

Some tips:
* Isolate each run
* run 3-5 trials per case (b/c models are non deterministic)
* graduate your evals - once a skill hits 100% pass rate agaisnt an evail, move that into "regression evals" that protect against backsliding
* Test across different harnesses
* Retire skills when agents can achieve your goals without using them.