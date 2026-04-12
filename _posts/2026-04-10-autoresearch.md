---
layout: post
title: "Autoresearch: Autonomous Hill-Climbing for Any Optimizable System"
categories: [AI, LLMs, Research, Agent Skill]
excerpt: "Run optimization experiments while you sleep"
pinned: true
---

TL;DR: With [Autoresearch][1], you are the research director rather than the scientist. Let AI agents run experiments while you sleep. The only requirement is having clear, unambiguous evals to optimize against.

## Table of Contents <!-- omit from toc -->

- [Autoresearch (Github)](#autoresearch-github)
  - [How ML optimization traditionally works](#how-ml-optimization-traditionally-works)
  - [Karpathy's Agentic Approach](#karpathys-agentic-approach)
  - [Design Constraints](#design-constraints)
- [Generalizing the pattern](#generalizing-the-pattern)
  - [Use cases](#use-cases)
  - [A/B Testing](#ab-testing)
- [Setting Up Autoresearch](#setting-up-autoresearch)
  - [Example 1: Reply rate optimization](#example-1-reply-rate-optimization)
  - [Example 2: Improving a Skill](#example-2-improving-a-skill)
  - [Autoresearch Agent Skill (Github)](#autoresearch-agent-skill-github)
- [Applications in the Physical World?](#applications-in-the-physical-world)
- [References](#references)

## Autoresearch ([Github](https://github.com/karpathy/autoresearch))

### How ML optimization traditionally works

In data science, you build a model, train it, and measure its performance with metrics like AUROC. To improve a model's performance, you might start by adjusting the learning rate, batch size, optimizer choice, or model architecture. You form a hypothesis ("a larger batch size might stabilize training"), run the experiment, interpret the result, form the next hypothesis, and so on. You could do a Grid search over different hyperparameters, then quickly find that the search space grows exponentially large with the number of parameters. People have come up with "smarter" optimization methods, like random search, Bayesian optimization, genetic algorithms, etc.

All of these have something in common: **you define the search space upfront**. You specify which parameters vary and what their ranges are. The algorithm searches *within* that space. A human still decides what dimensions matter before the search begins. Autoresearch sidesteps this limitation.

### Karpathy's Agentic Approach

Instead of a search space, Autoresearch gives the agent a file and tells it to make it better. The space of possible changes is whatever the agent can think of — including things no parameter grid would have included. The approach has three main components:

| File | Who touches it | What it contains |
| --- | --- | --- |
| `prepare.py` | Nobody | Fixed constants, data loading, tokenizer, evaluation harness — the ground truth |
| `train.py` | The agent | GPT model definition, optimizer, hyperparameters, training loop — everything is fair game |
| `program.md` | The human | Agent instructions — the "research goal" |

The agent runs this loop, forever, until you stop it:

```text
1. Read current git state
2. Form a hypothesis → modify train.py
3. git commit
4. uv run train.py > run.log 2>&1   (fixed 5-minute wall clock budget)
5. grep "^val_bpb:" run.log
6. If crashed: diagnose, fix or skip
7. Log to results.tsv: commit, val_bpb, memory, keep/discard, description
8. If improved: advance the branch
9. If not: git reset, try something else
```

In the original repo, the performance metric is `val_bpb` — validation bits per byte. Lower is better, and it's architecture-independent, so a change that doubles model size is compared fairly against one that just tweaks the learning rate. Each run takes 5 minutes. At 12 experiments per hour, you wake up to ~100 data points.

The thing being optimized is not a config file. It's the research artifact itself — the model architecture, optimizer choice, attention patterns, batch size schedule. This is beyond automated hyperparameter tuning: *"the LLM explores serially learning along the way, and can tool use and change code arbitrarily"* [[2]]. In round 2 of Karpathy's own runs, the agent implemented novel architecture changes — a smear gate and a backout skip connection — that actually helped. That's not hyperparameter tuning; that's new architecture.

### Design Constraints

**Fixed time budget.** Every experiment runs for exactly 5 minutes of wall-clock training time, regardless of model size, batch size, or architecture. This makes all experiments directly comparable — an agent that increases model depth by 2x gets the same budget as one that nudges a learning rate. It also means the agent finds the best model for *your specific hardware* in *that time window*, not in the abstract. This time budget essentially stops your training early and is not the perfect proxy for the final converged loss, but it's good enough to rank many candidates quickly.

**Single modifiable file.** The agent only touches `train.py`, which can contain anything from model architecture, optimizer, training loop, random helper functions, etc. This is the agent's playground. `prepare.py` is read-only — it contains the evaluation harness and fixed constants. This keeps the agent's degrees of freedom bounded and diffs reviewable. Critically, it means the evaluation instrument can't drift: the thing being measured stays constant while the thing being optimized changes.

**Scalar metric.** `val_bpb` is a single number. The keep/discard decision is **unambiguous**: lower is better, equal-or-worse gets reverted. No multi-objective tradeoffs, no human judgment calls in the loop.

**Never stop.** `program.md` explicitly instructs the agent not to pause and ask for confirmation. *"The human might be asleep, or gone from a computer and expects you to continue working indefinitely until manually stopped."* The loop only ends when you interrupt it. Asking "should I keep going?" destroys the overnight experiment.

**Simplicity criterion.** A marginal improvement that adds ugly complexity is not worth keeping. The agent is told: *"A 0.001 val_bpb improvement that adds 20 lines of hacky code? Probably not worth it. A 0.001 val_bpb improvement from deleting code? Definitely keep."* This prevents the failure mode where an agent accumulates technically-correct but unmaintainable changes.

## Generalizing the pattern

The original autoresearch focused on an ML problem. We can generalize the pattern:

> Give an agent a **single artifact to modify**, a **program that evaluates it**, a **fixed evaluation budget**, and a **scalar metric**. Let it hill-climb autonomously.

Instead of editing the artifact directly (the training code), you edit the instructions (`program.md`). You are now a research director — programming the process, not the experiments. And instead of defining the search space, you're defining the *strategy* — what kinds of changes to prioritize, what constraints to respect, when to be conservative.

The precondition that makes this work is that **the evaluation must be a script**. `uv run train.py > run.log && grep val_bpb run.log`. One command, one number. The agent closes the loop itself, with no human in the measurement path.

### Use cases

In the weeks since release, [awesome-autoresearch][3] (854 stars) has catalogued community applications across domains. The pattern has proven portable wherever someone could wire up an eval script:

| Domain | What the agent modified | Outcome | Author |
| --- | --- | --- | --- |
| **LLM training** | GPT model architecture, optimizer, hyperparameters | 20 improvements overnight on hand-tuned code | Karpathy [[1]] |
| **Production template engine** | Shopify's Liquid parse/render code | 53% faster, 61% fewer allocations — 93 automated commits | Tobi Lutke (Shopify CEO) [[4]] |
| **GPU kernel optimization** | CUDA/Triton kernels for any PyTorch model | 18 → 187 TFLOPS | RightNow AI [[5]] |
| **Voice agent prompts** | System prompts, evaluation criteria | Eval score 0.728 → 0.969 | Archie Sengupta [[6]] |
| **Bitcoin price prediction** | Formula structure for time-series forecasting | 50.5% RMSE improvement over power law, 328 experiments | Carlos Baquero [[7]] |
| **Earth system modeling** | Parameters of a climate/fire model | Fire correlation 0.09 → 0.65 | Dev Paragiri (UMD CS) [[8]] |
| **Sports analytics** | Biomechanics model for pitch velocity | R² 0.44 → 0.78 | Kyle Boddy (Driveline Baseball) [[9]] |
| **Ancient scroll ink detection** | Ink detection model for Vesuvius Challenge | Cross-scroll generalization nearly doubled | Vesuvius Challenge [[10]] |
| **Flaky test elimination** | Test code and fixture cleanup | 13 flaky tests fixed, 206 commits while the dev slept | Gianfranco Piana (Gumroad) [[11]] |

In the Shopify case, Tobi Lutke applied the same loop structure to a production Ruby gem. The agent edited real application code, ran a real benchmark, and committed 93 times overnight. The artifact being optimized was a template parser; the metric was parse+render time. Same loop, different domain. This is autoresearch having an impact in actual production code.

### A/B Testing

The loop can be applied to anything that can be measured with a metric and an API [[15]]. The agent modifies the artifact; the platform returns a quantifiable metric.

| Agent Nudges | Metric Optimized | Measurement Method |
| --- | --- | --- |
| Email copy | Reply rate | Email platform API (SendGrid, Mailchimp) |
| Landing pages | Conversion rate | A/B testing platform (Optimizely, VWO) |
| Chatbot / support scripts | CSAT or NPS | Post-conversation survey score |
| Push notifications | Click-through rate | Mobile analytics API |
| YouTube titles & thumbnails | Click-through rate | YouTube Analytics API |
| Subject lines | Open rate | Email platform API |
| Pricing pages | Checkout conversion | Analytics API |
| Product descriptions | Add-to-cart rate | E-commerce platform API |

These types of optimizations are usually done via A/B tests. Let your AI agent handle them.

## Setting Up Autoresearch

What you would need to use autoresearch for optimization:

- **Automatable evaluation.** The eval must return a number from a command-line call, no human in the loop. This is the binding constraint.
- **Reversible changes.** The agent needs to discard failed experiments cleanly. Git handles this trivially for code; other domains need an equivalent rollback mechanism.
- **A scalar metric.** If "better" requires judgment, the keep/discard step requires a human and the loop breaks. (The tennis match prediction case [[12]] hit this — the agent found reward hacking opportunities when the metric wasn't tight enough.)
- **Bounded scope.** There must be a `prepare.py` equivalent — a fixed evaluation instrument the agent cannot touch. Without it, the agent can optimize the metric by changing how it's measured.

And you don't even need to do this yourself. Just tell your coding agent what you want.

### Example 1: Reply rate optimization

Tell your coding agent [[15]]:

```text
Use the concept in the autoresearch repo to help me create a similar idea. Instead of
for validation loss and iterating on an ML model, do this for cold emails. I want to
optimize reply rate. Use the Instantly API, I'll have the necessary credentials in my
env file. Between each experiment, update the cold email copy. Lastly, put all of this
on github actions to run once every 4 hours. Save learnings to a resource.md file to
use as a reference. Give it everything it needs to run on autopilot. Build a simple
dashboard to visualize the progress and results over time.
```

Your coding agent will set up everything you need.

### Example 2: Improving a Skill

Note: May be superseded by built-in evals within the Claude [Skill-Creator skill][16].

Tell your coding agent:

```text
Goal: make diagrams

Evaluation/Constraints:
1. All diagrams legible and grammatically correct
2. Fits my color palette
3. Reads from left to right or top to bottom
4. No numbers

Measurement: Eval Test Suite -> get agent to create
Lever: Skill instructions

Use the autoresearch convention to build out a self-improving skill system for my
diagram-generator skill. The eval suite is the 4 constraints above. Every 2 minutes,
generate 10 diagrams for a specific function. Pass them through this test suite. Rate
how many pass. Then improve the prompt as necessary until the pass rate is 100%.

Scoring: 10 images x 4 criteria = 40 points total. 100% pass rate is 40/40.
```

### Autoresearch Agent Skill ([Github](https://github.com/uditgoenka/autoresearch))

This repo generalizes autoresearch even further by creating a set of agent skills for optimization.

Get started by installing the plugin:
```
/plugin marketplace add uditgoenka/autoresearch
/plugin install autoresearch@autoresearch
```

Then run it with
```
/autoresearch
Goal: Increase test coverage from 72% to 90%
Scope: src/**/*.test.ts, src/**/*.ts
Metric: coverage % (higher is better)
Verify: npm test -- --coverage | grep "All files"
```

Disclaimed: I have not tested this skill myself


## Applications in the Physical World?

Optimizations in the physical world wouldn't satisfy the previously mentioned criteria, but that constraint is eroding.

Robotic systems that run wet lab experiments autonomously already exist in early form. [Emerald Cloud Lab][13] and [Strateos][14] let researchers submit protocols programmatically and receive structured results. The barrier is the availability of infrastructure. Once a synthesis run, a materials stress test, or a fermentation cycle can be initiated by an API call and returns a JSON payload, the autoresearch loop applies directly.

The same logic extends further: a network of environmental sensors returning air quality readings, a robotics testbed where a policy runs and reports task completion rate, a precision agriculture deployment where irrigation schedules get evaluated against soil moisture telemetry. The evaluation oracle doesn't have to be a Python script — it has to be *something that returns a number without a human in the path*. Physical sensors, closed-loop labs, and simulation environments that mirror real hardware are all converging on that property.

## References

[1]: https://github.com/karpathy/autoresearch "karpathy/autoresearch — GitHub"
[2]: https://news.ycombinator.com/item?id=47291123 "HN: Autoresearch"
[3]: https://github.com/WecoAI/awesome-autoresearch "WecoAI/awesome-autoresearch — GitHub"
[4]: https://github.com/davebcn87/pi-autoresearch "pi-autoresearch — GitHub"
[5]: https://github.com/RightNow-AI/autokernel "RightNow-AI/autokernel — GitHub"
[6]: https://github.com/ArchishmanSengupta/autovoiceevals "autovoiceevals — GitHub"
[7]: https://github.com/CBaquero/BTCautoresearch "BTCautoresearch — GitHub"
[8]: https://paragiri.com/blog/2026/autoresearch-earth-system-models/ "Autoresearch for Earth System Models — Dev Paragiri"
[9]: https://x.com/drivelinekyle/status/2032242254035992610 "Kyle Boddy tweet — Driveline Baseball"
[10]: https://scrollprize.substack.com/p/we-are-cooking "Vesuvius Challenge: We Are Cooking"
[11]: https://gianfrancopiana.com/blog/autoresearch-flaky-tests "How I used autoresearch to fix Gumroad's flaky tests"
[12]: https://nickoak.com/posts/tennis-xgboost-autoresearch/ "XGBoost for tennis match prediction — Nick Oak"
[13]: https://www.emeraldcloudlab.com/ "Emerald Cloud Lab"
[14]: https://www.strateos.com/ "Strateos"
[15]: https://www.youtube.com/watch?v=4Cb_l2LJAW8 "Autoresearch Applications — YouTube"
[16]: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf "The Complete Guide to Building Skills for Claude — Anthropic"

1. [karpathy/autoresearch — GitHub](https://github.com/karpathy/autoresearch)
2. [HN: Autoresearch](https://news.ycombinator.com/item?id=47291123)
3. [WecoAI/awesome-autoresearch — GitHub](https://github.com/WecoAI/awesome-autoresearch)
4. [pi-autoresearch — GitHub](https://github.com/davebcn87/pi-autoresearch)
5. [RightNow-AI/autokernel — GitHub](https://github.com/RightNow-AI/autokernel)
6. [autovoiceevals — GitHub](https://github.com/ArchishmanSengupta/autovoiceevals)
7. [BTCautoresearch — GitHub](https://github.com/CBaquero/BTCautoresearch)
8. [Autoresearch for Earth System Models — Dev Paragiri](https://paragiri.com/blog/2026/autoresearch-earth-system-models/)
9. [Kyle Boddy tweet — Driveline Baseball](https://x.com/drivelinekyle/status/2032242254035992610)
10. [Vesuvius Challenge: We Are Cooking](https://scrollprize.substack.com/p/we-are-cooking)
11. [How I used autoresearch to fix Gumroad's flaky tests](https://gianfrancopiana.com/blog/autoresearch-flaky-tests)
12. [XGBoost for tennis match prediction — Nick Oak](https://nickoak.com/posts/tennis-xgboost-autoresearch/)
13. [Emerald Cloud Lab](https://www.emeraldcloudlab.com/)
14. [Strateos](https://www.strateos.com/)
15. [Autoresearch Applications — YouTube](https://www.youtube.com/watch?v=4Cb_l2LJAW8)
16. [The Complete Guide to Building Skills for Claude — Anthropic](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
