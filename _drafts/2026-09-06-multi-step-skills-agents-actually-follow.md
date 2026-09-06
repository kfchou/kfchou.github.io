---
layout: post
title: "Multi-Step Skills That Agents Actually Follow"
categories: [AI Coding, LLMs, Agents, Skills]
excerpt: "A multi-step skill usually fails not because the steps are wrong, but because the agent skips them, batches them, or declares itself done early. Here are eleven techniques for writing skills an agent can't easily short-circuit — and why each one works."
---

TL;DR - When a multi-step skill goes wrong, the steps are usually fine. The problem is that the agent skipped one, ran three at once, or announced it was finished before it actually was. Agents short-circuit for three reasons: they think they already know the flow from the *description*, nothing *forces* them to finish step N before starting N+1, and steps are *stated but not demanded* so a half-done step slips through. Every technique below attacks one of those three failure modes. Descriptions trigger, bodies instruct, checklists and todos track, gates enforce.

## Table of Contents <!-- omit from toc -->

- [Why multi-step skills short-circuit](#why-multi-step-skills-short-circuit)
- [1. Never summarize the workflow in the description](#1-never-summarize-the-workflow-in-the-description)
- [2. Give a checklist the agent ticks off — one TodoWrite item per step](#2-give-a-checklist-the-agent-ticks-off--one-todowrite-item-per-step)
- [3. Gate each step: only proceed when X passes](#3-gate-each-step-only-proceed-when-x-passes)
- [4. Make each completion criterion sharp AND demanding](#4-make-each-completion-criterion-sharp-and-demanding)
- [5. Set degrees of freedom by fragility](#5-set-degrees-of-freedom-by-fragility)
- [6. Linear steps are numbered lists, not flowcharts](#6-linear-steps-are-numbered-lists-not-flowcharts)
- [7. Progressive disclosure — but never hide what the current step needs](#7-progressive-disclosure--but-never-hide-what-the-current-step-needs)
- [8. Frame every step positively](#8-frame-every-step-positively)
- [9. For discipline-heavy sequences, close loopholes and list red flags](#9-for-discipline-heavy-sequences-close-loopholes-and-list-red-flags)
- [10. Handle per-step failure explicitly](#10-handle-per-step-failure-explicitly)
- [11. Test by watching an agent run it — with the weakest model you'll ship](#11-test-by-watching-an-agent-run-it--with-the-weakest-model-youll-ship)
- [The through-line](#the-through-line)
- [Sources / Further reading](#sources--further-reading)

## Why multi-step skills short-circuit

You write a skill with seven clear steps. You test it. The agent does step one, does step two, then jumps to "Done — I've completed the task" with steps three through six quietly skipped. The steps were correct. The agent just didn't run them.

This is the defining failure of multi-step skills, and it has three roots. **First, the agent thinks it already knows the flow.** If your description enumerates the steps, the model reads the description, forms a mental model of the procedure, and then under-executes the body because it believes it already has the plan. **Second, nothing forces sequence.** With no explicit blocker, "step 3" and "step 4" are just adjacent paragraphs, and a model optimizing for a finished-looking result will happily collapse or reorder them. **Third, steps are stated but not demanded.** A step that *describes* what good looks like ("produce a summary of changes") sets no bar the agent has to clear, so a half-hearted attempt passes as completion.

Every technique that follows attacks one of those three. If you keep the three failure modes in mind, most skill-authoring advice stops being a grab-bag of tips and starts looking like a small number of moves applied over and over. This is the multi-step companion to the ideas in [Tips to build good Agent Skills by Matt Pocock]({% post_url 2026-07-02-avoid-skill-hell %}) — that post is about discovery and pruning; this one is about getting the body of a procedural skill executed to the letter.

## 1. Never summarize the workflow in the description

This is the single biggest cause of step-skipping. The description's job is to answer *when to use this skill* — "Use when migrating a database schema," third person, discovery-only. The moment you write a description like "Use when migrating a schema: dump the DB, edit the migration, run it, verify, roll back on failure," you've handed the agent a four-step summary. It reads that, believes it now knows the recipe, and treats the detailed body as optional confirmation of a plan it already has. The recipe lives in the body — that is the part that actually gets followed. Keep the description a trigger and nothing more. If you catch yourself listing steps in a description, move them down.

## 2. Give a checklist the agent ticks off — one TodoWrite item per step

Working memory leaks. During a long, tool-heavy run — read a file, run a command, read the output, edit, run again — an early step can simply fall out of the model's active context by the time it's twenty tool calls deep. The fix is to externalize progress. Anthropic's skill-authoring guidance shows the copyable-checklist pattern: give the agent a literal checklist it reproduces and ticks off as it goes, so "have I done step 4?" is answerable by looking rather than remembering. In Claude Code the stronger move is one `TodoWrite` item per step. A todo list is a first-class artifact the harness keeps in view, and a step that has its own todo is one the agent visibly hasn't completed until it marks it done.

## 3. Gate each step: only proceed when X passes

A step that describes its own success is not the same as a step you cannot leave until you've succeeded. Compare "Step 2: fix the type errors" with "Step 2: fix the type errors. Do not proceed to Step 3 until `tsc` exits clean. If it still reports errors, return to the top of Step 2." The second is a gate. It creates a validator → fix → repeat loop the agent has to clear before it's allowed to advance, and an agent cannot rationalize its way past a gate it hasn't cleared the way it can talk itself past a mere description. Put an explicit blocker at the end of every step where correctness matters: name the check, name the pass condition, and name where to go back to on failure. Gates are how you force sequence — the second failure mode — into a skill that otherwise reads as reorderable paragraphs.

## 4. Make each completion criterion sharp AND demanding

The wording of a step's done-condition sets the amount of work the agent will do. A weak criterion permits lazy work: "produce a list of changes" is satisfied by three bullet points, so you get three bullet points. A sharp, demanding criterion forces the legwork: "every modified file is accounted for in the change list, and the list is verified against `git diff --name-only`" makes thoroughness the only way to pass. Sharpness (is it unambiguous?) and demand (does it require real work?) are different knobs and you want both — a criterion can be perfectly precise and still trivially satisfiable. When a step keeps producing shallow output, don't add more prose explaining what you want; tighten the criterion until shallow output no longer meets it.

## 5. Set degrees of freedom by fragility

Match how much you constrain a step to how fragile it is — the "narrow bridge versus open field" framing from Anthropic's docs. A fragile, order-dependent sequence — a database migration, a release cutover — is a narrow bridge: give it low freedom. Exact commands, exact order, "run this verbatim, do not add or modify flags." One wrong improvisation there corrupts state. An open-ended task — reviewing a diff, exploring a design space — is an open field: give it general direction and let it move. Get this backward in either direction and you pay. Over-constrain an open task and you burn tokens and suppress useful judgment; under-constrain a fragile sequence and the agent "helpfully" reorders or embellishes a step that had exactly one correct form. Freedom is a dial you set per step, not a global style.

## 6. Linear steps are numbered lists, not flowcharts

If the procedure is linear, write a numbered list. One action per numbered step, in order. It reads cleaner, and — more importantly — it's followed more reliably than the same logic drawn as a flowchart, because there's no branching for the agent to misinterpret and no "which path am I on" bookkeeping. Reserve flowcharts and decision trees for the genuinely non-obvious branch: "if the schema has foreign-key constraints, do A; otherwise do B." That's a real decision point worth diagramming. "First do X, then do Y, then do Z" is not a decision — it's a list, and dressing it up as a diagram only adds ways to get it wrong.

## 7. Progressive disclosure — but never hide what the current step needs

Progressive disclosure keeps a skill focused: push rarely-reached detail behind a one-level pointer ("if you need to handle the legacy format, see `legacy-format.md`") so the main path stays short and the agent's attention stays on the common case. Splitting off post-completion or edge-case steps genuinely helps concentrate the legwork. But there's a hard limit: never make the *current* step jump elsewhere for something it needs on every run. Each step's command, its rule, and its caveat must sit together, inline, where the step is. A step that says "run the deploy command (see appendix)" gets done wrong, because the agent either doesn't follow the pointer or follows it and loses the thread. Inline what every run touches; defer only what most runs never reach.

## 8. Frame every step positively

Tell the agent what to do, not what to avoid. "Write one-line comments" beats "don't write long comments." Negations are unreliable instructions for the same reason "don't think of an elephant" fails: to process the prohibition, the model first has to represent the banned behavior, and representing it makes it more available, not less. A skill full of "don't," "never," and "avoid" is planting the exact patterns it's trying to suppress. Where you can, convert every prohibition into its positive form — state the behavior you want in the affirmative. (The exception is deliberate loophole-closing in discipline-heavy skills, which is the next technique — and even there, you pair the prohibition with the positive behavior.)

## 9. For discipline-heavy sequences, close loopholes and list red flags

Some skills exist precisely to stop an agent from taking the shortcut it *wants* to take — commit discipline, test-first workflows, security checklists. For those, positive framing alone isn't enough; you have to name the specific escape hatches and slam them shut. Three tools work well together. A **rationalization table** pairs the excuse with reality ("'This change is too small to test' → small changes break things; write the test"). A **red-flags self-check** gives the agent a list of its own tell-tale thoughts that mean it's about to cheat ("if you're thinking 'I'll just do this one part first,' stop"). And an explicit line that **violating the letter is violating the spirit** kills the "I'm honoring the intent" defense before it's raised. Forbid the concrete shortcuts by name — don't batch the steps, don't skip verification because the result looks right — because "looks right" is exactly the judgment call these skills exist to override.

## 10. Handle per-step failure explicitly

The quietest way a multi-step skill produces a clean-looking wrong answer is a silent fallback: a step fails, the agent shrugs, substitutes a default or an empty result, and sails on through the remaining steps building on bad data. The output looks finished. It's wrong from step 3 onward and nothing flagged it. Prevent this by telling each step what to do when it fails, explicitly: write an error or a blocker, stop, and surface it — do not proceed with a guess. "If the migration dry-run fails, do not run the real migration; report the failure and halt" is a step that knows how to fail safely. A skill that only describes the happy path is trusting the agent to invent good failure behavior on the spot, and its instinct — keep going, produce something — is exactly wrong for a pipeline where later steps depend on earlier ones.

## 11. Test by watching an agent run it — with the weakest model you'll ship

You cannot tell whether a skill works by reading it. You find out by running it and watching. Dispatch it to a subagent, watch which steps it skips and — just as important — read what it *rationalized* while skipping them ("I'll consolidate steps 4 and 5 since they're related"). Each skip and each rationalization tells you exactly which counter to add: a gate here, a sharper criterion there, a loophole closed. Then re-run and see if the fix held. Crucially, test on the *weakest* model you intend to ship the skill on. A weaker model needs more explicit sequencing, harder gates, and tighter criteria than a stronger one — it has less slack to infer your intent. A skill that only holds together on the strongest model isn't robust; it's a skill that happens to work when the model is smart enough to paper over its gaps. Harden it against the weak model and it'll be bulletproof on the strong one.

## The through-line

Four verbs, four different jobs. **Descriptions trigger** — they get the skill discovered and invoked at the right moment, and nothing more. **Bodies instruct** — the actual recipe lives here, in the part that gets read and followed. **Checklists and todos track** — they externalize progress so no step falls out of working memory. **Gates enforce** — they block advancement until each step is genuinely done. A multi-step skill that keeps these separate — discoverable at the top, fully instructed in the body, tracked as it runs, and gated at every step where correctness matters — is one the agent can't easily skip, batch, or declare done early. Writing better steps matters less than writing steps the agent has no room to short-circuit.

## Sources / Further reading

- Anthropic — [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Anthropic — [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- Matt Pocock — [mattpocock/skills](https://github.com/mattpocock/skills)
- [Tips to build good Agent Skills by Matt Pocock]({% post_url 2026-07-02-avoid-skill-hell %}) — the companion post on skill discovery, structure, and pruning
