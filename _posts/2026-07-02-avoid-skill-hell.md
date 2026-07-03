---
layout: post
title: "Avoid Skill Hell -- Tips of good Agent Skills by Matt Pocock"
categories: [AI Coding, LLMs, Claude Code, Agent Skill]
---

These are notes taken from a [talk](https://www.youtube.com/watch?v=UNzCG3lw6O0) by Matt Pocock, where he shares his philosophy in designing agent skills. Matt is the author of the popular agent skill repository [mattpocock/skills](https://github.com/mattpocock/skills)(154k stars).

## 1. Trigger
The keyword `disable-model-invocation` in the skill file header can prevent your skill from being invoked by models, making them user-invoked only by using the command syntax: `/my-skill`

Why would you want this? User-invocation removes the ambiguity of knowing when skills are correctly triggered. The popular obra/superpowers skill repository is frequently updated, but most of those updates concerns with tweaking the skill description to make sure they're invoked at the right times.

To avoid this ambiguity, Matt would rather put cognitive load on users and make his skills all **user-invoked**.

## 2. Structure
Each skill file should have
1. step-by-step procedures
2. supporting information/references - templates, definitions, etc

Each skill file should be as small as possible. Why?
* Fewer tokens
* More maintainable
* More readable

Think about the different action branches of the skill. Many skills only have a single branch, but some have many. If there are many branches, use pointers to point to references to keep the file small.

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
* Massive skill files
* Repeating yourself
* Sediment -- accumulation over time, maybe by multiple users.
* No-ops -- things inside the skill that actually doesn't influence the Agent's behavior

Tips:
* Use deletion tests to prune
* See [mattpocock/writing-great-skills](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md)