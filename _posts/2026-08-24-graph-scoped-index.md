---
layout: post
title: "Your Knowledge-Base Index Is O(N). Your Query Isn't."
categories: [LLMs, RAG, Knowledge Management, Retrieval]
excerpt: "A flat whole-corpus index makes every query pay to scan the entire knowledge base just to decide what to read. If your documents already declare their relationships in frontmatter, they form a graph — and you can route over the query's neighborhood instead of the whole corpus. A measured study: ~49% less routing context, an honest recall gap with two distinct failure modes, and the two fixes that close most of it."
---

TL;DR — If you route LLM queries over a flat index built across your whole knowledge base, the routing surface is **O(total corpus size)**: every query, however narrow, makes the model scan a summary line for every document you have, just to pick the handful it will actually read. But a curated KB isn't a bag of documents — it's a **graph**, and the relationships are usually already sitting in your frontmatter. Extract that graph, resolve the query to a few entry nodes, fan out a couple of hops, and route over *only that neighborhood*. On a real knowledge base — a few hundred analysis documents plus their source captures — this cut routing context **~49%** and end-to-end context **~44%** per query. The catch is a measurable recall gap with two distinct failure modes; both are addressable, and I'll show which is which. This post is the method and the numbers, including where the flat index still wins.

## Table of Contents <!-- omit from toc -->

- [The problem: flat indexes make every query pay for the whole corpus](#the-problem-flat-indexes-make-every-query-pay-for-the-whole-corpus)
- [The idea: route over the neighborhood, not the corpus](#the-idea-route-over-the-neighborhood-not-the-corpus)
- [How the graph is built: edges from frontmatter](#how-the-graph-is-built-edges-from-frontmatter)
- [The experiment](#the-experiment)
- [Results: routing context](#results-routing-context)
- [Results: scaling — the honest half of the story](#results-scaling--the-honest-half-of-the-story)
- [Results: the recall gap, and its two failure modes](#results-the-recall-gap-and-its-two-failure-modes)
- [Fixing entry resolution: tags to find the door, not to build the hallways](#fixing-entry-resolution-tags-to-find-the-door-not-to-build-the-hallways)
- [Does the smaller surface make the model pick better?](#does-the-smaller-surface-make-the-model-pick-better)
- [Honest limitations](#honest-limitations)
- [How to adopt it](#how-to-adopt-it)

## The problem: flat indexes make every query pay for the whole corpus

Most retrieval setups over a curated knowledge base share one pattern: build a single index over *everything*, hand the model that index as a routing surface, and let it decide what to read. Each document contributes a short "routing card" — a title, a summary line, a few tags — and the model scans all of them to choose which full documents to open. It's simple, it's deterministic, and it works.

Until the corpus grows. The trouble is that the routing surface is **O(total corpus size)**. Ask a narrow question — "what changed for FAKE-CO last quarter?" — and the model still reads the routing card for every document in the store, including the hundreds about other companies, just to decide which five are relevant. Double the corpus and you double the routing bill on *every* query. The answer didn't get bigger; the tax on finding it did.

Concrete numbers from the KB I studied — a curated investing knowledge base of a few hundred documents (filed analyses plus the raw and processed source captures they cite): the flat routing surface is roughly **66,000 tokens**. That is loaded on every query, before a single real document is read. It's affordable today — 66k against a million-token window is nothing — but it's a *per-query* cost that grows linearly with the corpus, and most of it is pure distraction: on any given query, the overwhelming majority of those cards describe documents that have nothing to do with the question.

## The idea: route over the neighborhood, not the corpus

Curated KBs are not bags of documents — they're **graphs**. The documents already declare their relationships: this analysis *cites* those sources; this earnings capture *affects* that entity; this note is *grounded in* that thesis. In a well-structured KB those declarations live in the frontmatter as machine-readable fields — edges we haven't been treating as edges.

So instead of indexing the whole corpus, do this:

1. Extract a graph from the frontmatter.
2. Resolve the query to one or more **entry nodes** — the entities or topics it names.
3. Fan out N hops from those entry nodes to get a **neighborhood**.
4. Build the routing index over *only that neighborhood*.

Routing context becomes **O(relevant subgraph)** instead of O(corpus).

```
Flat:   query ─▶ [scan ALL ~450 routing cards] ─▶ pick ─▶ read
Graph:  query ─▶ resolve entry nodes ─▶ N-hop neighborhood
              ─▶ [scan ~195 routing cards] ─▶ pick ─▶ read
```

Note what does *not* change: the routing cards themselves. The flat index is still the source of truth for what each card says. The graph only decides *which* cards the model scans. That keeps the change additive — you can bolt it on in front of an existing index and rip it out with a flag.

## How the graph is built: edges from frontmatter

The methodology hinges on one decision: **frontmatter is authoritative for edges.** Edges are built only from structured fields, never from inline prose links. This is deterministic, cheap, and testable — and it bounds recall in a way I'll be explicit about later. Nothing here needs an LLM; the graph is pure text extraction.

In the KB I studied, the cross-document frontmatter fields map to typed edges like this:

| Frontmatter field | Edge | Meaning |
|---|---|---|
| `sources: [...]` | **cites** | this analysis was built from those documents |
| `affected_securities: [...]` | **affects_security** | this capture bears on those entities |
| `affected_theses: [...]` | **affects_thesis** | this capture bears on those theses |
| `thesis_categories: [...]` | **grounded_in** | this document rests on those theses |
| `raw_path: ...` | **derived_from** | this processed doc came from that raw capture |
| `promoted_to: [...]` | **promoted_to** | this capture was promoted into a note |
| `invalidated: [...]` | **invalidated_by** | this claim was overturned by that evidence |

Extracted over the real corpus, that's on the order of **810 nodes and ~1,220 typed directed edges**. Two details matter for anyone implementing this:

- **Resolution is fiddly.** Pointers are inconsistent — a thesis is referenced sometimes by its slug (`fake-co-infrastructure`), sometimes by its date-prefixed filename stem. A correct resolver tries slug first, then filename-stem, then path. Getting `sources:` resolution right is the single highest-value, easiest-to-botch part; test it explicitly.
- **Mega-hubs will wreck you if you let them.** Real KBs have a few documents that everything points at — in this one, a central sector thesis with degree ~250. Fanning *through* such a hub during traversal pulls in half the corpus and defeats the entire purpose. The fix is **hub-damped BFS**: traversal is allowed to *reach* a hub but not *fan out through* it once its degree exceeds a cap. This one refinement is what makes graph-scoping viable on a hub-dominated KB at all.

## The experiment

A KB whose analyses cite their sources comes with a **free benchmark**. Every filed analysis records, in its frontmatter `sources:` field, the exact set of documents that answered its question. That's a `(query, gold-retrieval-set)` pair, already labeled by whoever wrote the analysis. Across the corpus: **34 scored queries, 162 gold documents** (mean ~4.8 gold docs per query, range 1–28). The query text is the analysis's title, filename stem, summary, and tags; the gold set is each declared source resolved to an indexable node.

One design constraint matters. An analysis's own citations *are* the gold edges — so seeding the graph traversal from the analysis node itself would walk straight down its own `cites` edges to the gold, a circular win. Every query is therefore run against a **held-out graph**: the benchmarked analysis's outgoing edges are withheld, and the analysis node is never used as a seed. The graph method has to reach the gold documents through *other* documents' frontmatter. That's what makes the recall numbers below trustworthy.

Per query, per method (flat = A, graph-scoped = B), three things were measured:

- **Routing context size** — the total tokens of routing cards the model must scan. Exact and deterministic. A = all cards; B = only the neighborhood's cards.
- **Recall ceiling** — the fraction of gold documents reachable in the surface *at all*. A is 1.0 by construction. For B this isolates the traversal limit from the router's own mistakes: if a gold doc isn't in the neighborhood, no router can pick it.
- **Pick quality** — given each surface, how well does the picker actually select the gold? Precision / recall / F1 / pollution (non-gold docs picked), same picker on both sides.

A note on honesty up front: the first two are fully deterministic and need no model. The third does — and the first pass of this study had no live LLM available, so it used a lexical (BM25) picker as a stand-in. That turned out to matter a lot, and I come back to it below.

## Results: routing context

At full corpus, with the recommended configuration (2-hop traversal, hub-cap 40):

| Metric | Flat (A) | Graph (B) | Δ |
|---|---:|---:|---:|
| Routing context / query | 66,180 tok (constant) | 33,941 mean / 46,742 median | **−49% mean / −30% median** |
| End-to-end context / query (routing + docs read) | 82,049 tok | 46,098 tok | **−44%** |
| Recall ceiling | 1.000 | 0.810 | −0.19 |

The headline is a **~49% cut in routing context and ~44% end-to-end** — measured exactly, on a corpus that is close to the *worst case* for this technique (more on why in the next section).

The mean-vs-median gap reflects a real bimodality: queries that resolve into the dense core of the KB still pull ~47k of the 66k index (only ~30% off), while peripheral, low-connectivity queries pull far less and drag the mean down. The "49%" is flattered by the easy queries; the typical dense-core query saves closer to 30%. Both numbers are real; I report both.

The configuration is a tradeoff — the full frontier shows it more honestly than any single point:

![The scoping tradeoff: routing-context reduction vs recall ceiling across every hop-count and hub-cap setting. 1-hop saves the most but reaches the least gold; 3-hop reaches the most gold but saves the least. The circled 2-hop, hub-cap-40 point is the knee of the curve.](/assets/2026-08-24-graph-scoped-index/tradeoff-frontier.png)

One hop saves 71% but reaches only ~60% of the gold. Three hops reach ~86% of the gold but save only 30%. **Two hops with a hub-cap of 40 is the knee** — 55% routing reduction at an 81% recall ceiling. And notice the ceiling *plateaus* around 0.85 even at three hops: that residual ~15% is gold reachable only through the held-out analysis's own edges or through prose links the frontmatter never captured — a hard floor for a frontmatter-only method, which is the topic of the recall section.

## Results: scaling — the honest half of the story

The tempting story: flat is O(N), graph is O(1), graph wins by 10×, margin grows forever. Half true.

This KB is **one dense topic** — nearly everything is about a single sector, and the largest connected component is a majority of the graph. On a mono-thematic KB, the query's neighborhood is a large *fraction* of the whole corpus. So as documents accrete, B grows too, and its advantage holds *steady* rather than widening:

![Empirical scaling: as captures accrete into one topic, flat routing context grows strictly linearly (~148 tokens per document), while graph routing context also grows — because every new capture points into the same dense cluster. The graph's advantage erodes slowly from 53.5% to 48.8%.](/assets/2026-08-24-graph-scoped-index/scaling-empirical.png)

Flat grows strictly linearly — about 148 tokens per document added. Graph grows too, because every new capture declares relationships pointing *into* the same dense cluster, so it lands in most queries' neighborhoods. The graph's advantage erodes gently, from ~53.5% down to ~48.8% over the measured range. **On a single-topic KB, graph-scoping is a stable ~50% cut, not an asymptote to flat.** If someone sells you the 10×, this is the number they're not showing you.

Where the O(N)-vs-O(neighborhood) argument *does* pay off dramatically is when the corpus grows by **adding separable topics** rather than deepening one. Frontmatter edges are within-topic: a document in one sector doesn't declare `affected_securities` in an unrelated one. So a query about topic *t* has a neighborhood bounded by *t*'s size, no matter how many other topics exist alongside it.

![Projection: if the KB diversifies into T equally-sized, edge-separable topics, flat routing context grows linearly in T (scan every topic's index) while graph routing stays bounded by one topic. Reduction goes from 49% at one topic to 74% at two, 83% at three, and ~90% at five. Today's KB sits at the T=1 point.](/assets/2026-08-24-graph-scoped-index/scaling-projection.png)

Model a KB of T equally-sized, edge-separable topics. Flat scans every topic's index — O(T). Graph stays bounded to the query's topic — O(1). The reduction goes 49% at one topic → 74% at two → 83% at three → ~90% at five. The single assumption here — that topics are edge-separable — is stated, not assumed away. Today the KB sits at the T=1 point, which is exactly why the present win is ~2× and not 10×. **The value is real today and compounds as coverage broadens.**

## Results: the recall gap, and its two failure modes

Scoping has a price: a document the flat index would have surfaced by topic can be unreachable in the graph neighborhood. The gap is **two distinct failure modes**, and keeping them separate determines what you do about each.

![Left: per-query routing reduction is bimodal — a cluster of dense-core queries around 20–30% and a smaller cluster of peripheral queries at 70–100%, with mean 49% and median 29%. Right: recall outcome across the 34 queries — 23 fully reachable, 7 partially reachable, and 4 that miss entirely, all four being zero-seed entry-resolution failures.](/assets/2026-08-24-graph-scoped-index/recall-distribution.png)

Against the held-out graph, of 34 queries: **23 are fully reachable, 7 partial, 4 miss entirely.** The two failure modes:

- **Entry-resolution misses (~12%).** All four complete misses are *zero-seed* queries: the query text named no entity the resolver could catch, so traversal never started. This is a problem with the *front door*, not the graph. It's fixable without touching the graph at all — with better query resolution, or with a **flat-scan fallback**: if nothing resolves, fall back to the full flat index. With that fallback, the graph method is **never worse than flat, only sometimes equal.**
- **Frontmatter-only traversal gap (~8% of gold on resolved queries).** Among queries that *do* seed, the recall ceiling is ~0.92 — the missing ~8% is gold connected only through inline prose links or the held-out edges, invisible to a frontmatter-only traversal. This is genuinely unreachable by the graph as built, and it's the target of a **completeness auditor**: a pass that proposes the missing structured edges (turning a prose-only dependency into a real `sources:`/`affects_*` edge), lifting the ceiling back toward flat's 1.0.

This is precisely where the flat index wins — it catches by global topic-scan what a scoped traversal misses. The cost is bounded, measurable, and addressable — not inherent.

## Fixing entry resolution: tags to find the door, not to build the hallways

The entry-resolution miss is the more fixable of the two, so a follow-up experiment went after it directly. The obvious lever is the `tags:` frontmatter field, which every document already has. The tag-degree distribution is a useful warning first: of 405 distinct tags, most are singletons, but a handful are mega-tags sitting on 30–40 documents each. Naively linking every pair of co-tagged documents would create **~4,000 edges — over 3× the entire frontmatter graph** — almost all radiating from those few mega-tags. That's the mega-hub explosion all over again.

The two uses:

- **Tags for entry (finding the door).** Use tags only as an *entry-resolution* vocabulary — a way to find a seed node when the ticker/slug resolver comes up empty — and skip the mega-tags. This closed **100% of the entry-resolution misses** (every zero-seed query now resolves), lifting the recall ceiling **+0.094**, at a cost of only **+9% routing context** (still a 41% cut versus flat). The mechanism is honest: tags give the query a *foothold seed*, and the existing frontmatter edges do the actual reaching — only one of the recovered gold docs was directly tag-seeded; the rest were reached by normal traversal from the tag-seeded node.
- **Tags for traversal (building the hallways).** Use co-tag links as *edges* you traverse. This buys a little more recall at 4–7× the token cost, and in its naive form it collapses the routing reduction from ~46% to ~12% — it rebuilds the mega-hub and erases the entire point of scoping.

![Recall-vs-cost frontier for tag designs. The surgical tag-for-entry design (D1s) is a near-vertical gain: +0.094 recall ceiling for only +3.7k tokens. Every tag-traversal design marches rightward — more expensive — for diminishing recall, with the naive co-tag design landing close to the flat-scan cost.](/assets/2026-08-24-graph-scoped-index/tag-fallback-frontier.png)

The frontier says it in one picture: surgical tag-for-entry is a near-vertical move (recall for almost no cost); every traversal variant marches rightward (expensive) for shrinking gains. **Use tags to find the entry point, not to build edges.**

## Does the smaller surface make the model pick better?

The sharpest reversal in the study is on *pick quality* — whether a smaller routing surface makes the model choose better documents, not just cheaper ones. The intuition is that fewer plausible-but-wrong cards means fewer distractors. The first pass couldn't confirm it: with only a lexical (BM25) picker available, the graph surface actually scored *worse* on precision (F1 0.32 vs 0.40). A bag-of-words picker can't exploit distractor-reduction — it doesn't reason over the surface, so a smaller surface just means fewer chances to keyword-match the gold.

The follow-up re-ran it with an actual LLM router, using a deliberately blind protocol: one fresh, isolated agent per (query, surface) pair, each shown *only* its query and one surface's cards, never the gold and never the other surface. Across 12 queries (24 agents), the result flips:

| | Flat (A) | Graph (B) |
|---|---:|---:|
| Macro-F1 | 0.541 | **0.587** |
| Micro-F1 (pooled) | 0.454 | **0.593** |
| Pollution (non-gold picked) | 4.92 | **3.67** |

The smaller surface produces **at-least-as-good and on-aggregate better** picks, with less pollution — reversing the lexical-proxy negative. The mechanism is illuminating: the biggest wins were on large, granular-source queries. On one query whose gold was 27 individual earnings captures, the flat-surface router picked the tidy summary dossiers and scored **0.0**; the neighborhood-surface router picked the actual cited captures and scored **0.56** — because in the scoped neighborhood, those captures *dominate* the surface and are the obvious granularity to pick.

The caveats, stated plainly because they matter:

- **By per-query win count it's a tie** (B wins 3, ties 6, A wins 3). B's aggregate edge is concentrated in a few large-k queries; one of them moves the pooled micro-F1 substantially.
- **Single model, n=12.** The router and the (deterministic) scorer are the same model family; there's no independent evaluator. This is directional evidence, not a controlled trial.
- **Part of B's edge is "right granularity," not purely "fewer distractors."** The benchmark counts granular captures as gold, and B's neighborhood is denser in exactly those. That's a real retrieval-quality signal, but it's entangled with the neighborhood's composition. I flag it rather than net it out.

So: treat the 44–49% context reduction as solid, and the precision upside as promising-but-directional. I'd rather tell you which number is which.

## Honest limitations

- **The recall gap is real.** ~8% of gold on resolved queries is unreachable via frontmatter edges alone, and the ceiling plateaus around 0.85 even at three hops. The completeness auditor is the intended backstop, but it isn't free and it's propose-only.
- **Entry resolution is deliberately simple** (ticker + slug-word match, plus surgical tag-for-entry). A better resolver shrinks the miss rate; a vaguer query inflates it. Reported as measured, not tuned to flatter the method.
- **Pick quality rests on a single-model, n=12 run.** The reversal is encouraging but wants an independent-model replication before anyone calls it settled.
- **The scaling win is back-loaded.** Today's KB is mono-thematic, so the present win is a stable ~2×. The 74–90% projection depends on the corpus diversifying into edge-separable topics — a stated assumption the current corpus can't yet confirm empirically.
- **Gold = declared `sources:`.** The benchmark measures retrieval against *recorded* dependencies. If an analysis silently leaned on a document it never cited, neither method is credited or penalized. That's a benchmark-definition choice, not a bug.

## How to adopt it

If you're routing LLM queries over a flat whole-corpus index, you're paying O(N) on every query for an answer that lives in O(neighborhood). If your documents already carry structured relationships — and curated KBs usually do — a graph-scoped index turns that routing bill from linear-in-corpus into bounded-by-topic. The practical recipe, in the order the evidence supports:

1. **Extract the graph from frontmatter** and route over the query's 2-hop, hub-damped neighborhood. Budget most of your implementation care for the resolver and `sources:` resolution — that's where correctness lives.
2. **Keep a flat-scan fallback.** When entry resolution returns nothing, fall back to the full index. This caps the downside: the graph method is then never worse than flat, only sometimes equal.
3. **Add surgical tag-for-entry** ahead of the fallback — tags to find the entry point, skipping mega-tags. It closes the entire entry-resolution failure mode for ~9% more context and makes the expensive fallback fire far less often. Do *not* add tag traversal edges; they rebuild the mega-hub.
4. **Run a completeness auditor** as the recall backstop for the frontmatter-only gap — a propose-only pass that surfaces prose-only dependencies as candidate structured edges for a human to accept.

The whole thing is additive and reversible: the graph selects which cards the model scans; the existing index still defines what each card says; a feature flag reverts to flat instantly. The context reduction is solid (~44–49%), the precision upside is promising-but-directional, and the recall cost is bounded and measurable. Not a capacity fix. Not a 10× (yet). Measure both sides and don't assume the gap away.
