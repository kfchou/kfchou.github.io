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
- [The experiment](#the-experiment)
- [Results: routing context](#results-routing-context)
- [Results: scaling as the wiki grows](#results-scaling-as-the-wiki-grows)
- [Results: the recall gap, and its two failure modes](#results-the-recall-gap-and-its-two-failure-modes)
- [Fixing entry resolution: tags for seeding, not for traversal](#fixing-entry-resolution-tags-for-seeding-not-for-traversal)
- [Does the smaller surface make the model pick better?](#does-the-smaller-surface-make-the-model-pick-better)
- [Three ways to scope: flat, tiered, graph](#three-ways-to-scope-flat-tiered-graph)
- [Limitations](#limitations)
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

Routing context becomes **O(relevant subgraph)** instead of O(wiki).

```
Flat:   query ─▶ [scan ALL ~450 routing cards] ─▶ pick ─▶ read
Graph:  query ─▶ resolve entry nodes ─▶ N-hop neighborhood
              ─▶ [scan ~195 routing cards] ─▶ pick ─▶ read
```

One thing deliberately doesn't change: the routing cards themselves. Each page still contributes the same card — its title, summary, and tags. Graph-scoping only changes *which* cards are gathered into the index: a flat index gathers every page's card, while the graph gathers only the neighborhood's. Because the cards are untouched, graph-scoping is purely additive: it inserts the neighborhood-selection step ahead of index-building and changes nothing else, so a single flag disables it and routing falls back to the full flat scan.
<I still don't like this; will come back to it later>

## The experiment

To evaluate whether graph routing pays off, we first define *retrieval quality*: how well a method recovers the documents relevant to a query. We quantify it with three standard measures — precision, recall, and F1. For a query, let the *gold set* be the documents that actually answer it and the *retrieved set* be the documents a method returns:

- **Precision** — the fraction of retrieved documents that are relevant: |retrieved ∩ gold| / |retrieved|.
- **Recall** — the percentage of relevant documents retrieved: |retrieved ∩ gold| / |gold|.
- **F1** — the harmonic mean of precision and recall: 2 · precision · recall / (precision + recall), high only when both are.

Since a research wiki already contains sources and links, it is easy to build a gold set to benchmark against.
Every filed analysis lists the documents it was built from in its frontmatter `sources:` field. That turns each analysis into a labeled example: the analysis is the query, and its listed sources are the correct answer. Across the wiki, the analyses yield **34 scored queries and 162 gold documents**, about 4.8 per query on average and ranging from 1 to 28. For each query, we take the text from the analysis's title, filename, summary, and tags, and resolve its listed sources to indexable nodes as the correct answer.
This benchmark has one subtlety to handle. Each analysis cites the very documents we grade it against, so seeding the traversal from the analysis's own node would be circular: it would follow that node's `cites` edges straight to the answer for a perfect but meaningless score. To avoid this, every query runs against a **held-out graph** — the analysis under test has its outgoing edges removed and is never used as a seed. The method must reach the correct documents through other pages' frontmatter instead. That is what makes the recall numbers below trustworthy.

Per query, per method (flat = A, graph-scoped = B), three things were measured:

- **Routing context size** — the total tokens of routing cards the model must scan. Exact and deterministic. A = all cards; B = only the neighborhood's cards.
- **Recall ceiling** — the fraction of gold documents reachable in the surface *at all*. A is 1.0 by construction. For B this isolates the traversal limit from the router's own mistakes: if a gold doc isn't in the neighborhood, no router can pick it.
- **Pick quality** — given each surface, how well does the picker actually select the gold? Precision / recall / F1 / pollution (non-gold docs picked), same picker on both sides.

The first two are fully deterministic and need no model; the third does. The first pass of this study had no live LLM available, so I used a lexical (BM25) picker as a stand-in. That substitution significantly affected the pick-quality results, as discussed below.

## Results: routing context

At full wiki size, with the recommended configuration (2-hop traversal, hub-cap 40):

| Metric | Flat (A) | Graph (B) | Δ |
|---|---:|---:|---:|
| Routing context / query | 66,180 tok (constant) | 33,941 mean / 46,742 median | **−49% mean / −30% median** |
| End-to-end context / query (routing + docs read) | 82,049 tok | 46,098 tok | **−44%** |
| Recall ceiling | 1.000 | 0.810 | −0.19 |

Two headline numbers, both measured exactly: a **~49% cut in routing context and ~44% end-to-end**. Both come from a wiki close to the *worst case* for this technique — the next section explains why.

The gap between mean and median is real bimodality. Queries that land in the dense core of the wiki still pull ~47k of the 66k index — only ~30% off — while peripheral, low-connectivity queries pull far less and drag the mean down. So the 49% is flattered by the easy queries: a typical dense-core query saves closer to 30%. Both figures are honest, so I report both.

The configuration is a tradeoff — the full frontier shows it more honestly than any single point:

![The scoping tradeoff: routing-context reduction vs recall ceiling across every hop-count and hub-cap setting. 1-hop saves the most but reaches the least gold; 3-hop reaches the most gold but saves the least. The circled 2-hop, hub-cap-40 point is the knee of the curve.](/assets/2026-08-24-graph-scoped-index/tradeoff-frontier.png)

One hop saves 71% but reaches only ~60% of the gold; three hops reach ~86% but save only 30%. **Two hops with a hub-cap of 40 is the knee** — a 49% routing cut at an 81% recall ceiling. The ceiling also *plateaus* near 0.85 even at three hops. That last ~15% is gold reachable only through the held-out analysis's own edges or through prose links the frontmatter never captured — a hard floor for any frontmatter-only method, and the subject of the recall section.

## Results: scaling as the wiki grows

A naive projection says flat is O(N) and graph is O(1), so the margin between them should grow without bound. It doesn't, at least not on a wiki shaped like this one.

This wiki is **one dense topic**: nearly everything concerns a single subject area, and the largest connected component covers most of the graph. On a mono-thematic wiki, a query's neighborhood is a large *fraction* of the whole. So as the wiki grows, B grows with it, and its advantage stays *steady* rather than widening:

![Empirical scaling: as documents accrete into one topic, flat routing context grows strictly linearly (~148 tokens per document), whereas graph routing context also grows — because every new document points into the same dense cluster. The graph's advantage erodes slowly from 53.5% to 48.8%.](/assets/2026-08-24-graph-scoped-index/scaling-empirical.png)

Flat grows strictly linearly, about 148 tokens per document. Graph grows too: every new document points *into* the same dense cluster, so it lands in most queries' neighborhoods. Its advantage erodes gently over the measured range, from ~53.5% to ~48.8%. **On a single-topic wiki, graph-scoping is a stable ~50% cut, not an asymptote to flat.**

The O(N)-vs-O(neighborhood) argument pays off dramatically in a different kind of growth: when the wiki adds **separable topics** rather than deepening one. Frontmatter edges stay within a topic — a document in one subject area doesn't declare `affected_entities` in an unrelated one — so a query about topic *t* has a neighborhood bounded by *t*'s size, however many other topics sit alongside it.

![Projection: if the wiki diversifies into T equally-sized, edge-separable topics, flat routing context grows linearly in T (scan every topic's index) while graph routing stays bounded by one topic. Reduction goes from 49% at one topic to 74% at two, 83% at three, and ~90% at five. Today's wiki sits at the T=1 point.](/assets/2026-08-24-graph-scoped-index/scaling-projection.png)

Model a wiki of T equally-sized, edge-separable topics. Flat scans every topic's index, O(T); graph stays bounded to the query's topic, O(1). The reduction climbs 49% at one topic → 74% at two → 83% at three → ~90% at five. Today the wiki sits at the T=1 point, which is why the present win is ~2× rather than 10×. **The value is real today and compounds as coverage broadens.**

## Results: the recall gap, and its two failure modes

Scoping has a price: a document the flat index would have surfaced by topic can be unreachable in the graph neighborhood. The two failure modes require different fixes:

![Left: per-query routing reduction is bimodal — a cluster of dense-core queries around 20–30% and a smaller cluster of peripheral queries at 70–100%, with mean 49% and median 29%. Right: recall outcome across the 34 queries — 23 fully reachable, 7 partially reachable, and 4 that miss entirely, all four being zero-seed entry-resolution failures.](/assets/2026-08-24-graph-scoped-index/recall-distribution.png)

Against the held-out graph, of 34 queries: **23 are fully reachable, 7 partial, 4 miss entirely.** The two failure modes:

- **Entry-resolution misses (~12%).** All four complete misses are *zero-seed* queries: the query text named no entity the resolver could catch, so traversal never started. This is a problem with the *front door*, not the graph. It's fixable without touching the graph at all — with better query resolution, or with a **flat-scan fallback**: if nothing resolves, fall back to the full flat index. With that fallback, the graph method is **never worse than flat, only sometimes equal.**
- **Frontmatter-only traversal gap (~8% of gold on resolved queries).** Among queries that *do* seed, the recall ceiling is ~0.92. The missing ~8% is gold linked only through inline prose or the held-out edges, so a frontmatter-only traversal can't see it. The graph as built genuinely can't reach it — which is the job of a **completeness auditor**: a pass that spots those prose-only dependencies and proposes them as real `sources:`/`affects_*` edges, lifting the ceiling back toward flat's 1.0.

This is exactly where the flat index wins: a global topic-scan catches what a scoped traversal misses. But the cost is bounded, measurable, and addressable, not inherent.

## Fixing entry resolution: tags for seeding, not for traversal

The entry-resolution miss is the more fixable of the two, so I ran a follow-up experiment to go after it. The obvious lever is the `tags:` field every document already has. But the tag-degree distribution is a warning: of 405 distinct tags, most are singletons, while a handful are mega-tags sitting on 30–40 documents each. Naively linking every pair of co-tagged documents would create **~4,000 edges — over 3× the entire frontmatter graph** — almost all of them radiating from those few mega-tags. That is the mega-hub explosion all over again.

Tags can play two roles here, with very different outcomes:

- **Tags for entry.** Use tags only as an *entry-resolution* vocabulary — a way to find a seed node when the id/slug resolver comes up empty — and skip the mega-tags. This closed **100% of the entry-resolution misses**: every zero-seed query now resolves. It lifted the recall ceiling by **+0.094** for only **+9% routing context**, still a 41% cut versus flat. And the mechanism is honest: the tag only supplies a *foothold seed*, and the existing frontmatter edges do the actual reaching. Only one recovered gold doc was directly tag-seeded; the rest came from normal traversal out of the tag-seeded node.
- **Tags for traversal.** Use co-tag links as *edges* you traverse. This buys a little more recall at 4–7× the token cost. In its naive form it collapses the routing reduction from ~46% to ~12%, rebuilding the mega-hub and erasing the entire point of scoping.

![Recall-vs-cost frontier for tag designs. The surgical tag-for-entry design (D1s) is a near-vertical gain: +0.094 recall ceiling for only +3.7k tokens. Every tag-traversal design marches rightward — more expensive — for diminishing recall, with the naive co-tag design landing close to the flat-scan cost.](/assets/2026-08-24-graph-scoped-index/tag-fallback-frontier.png)

On the frontier, tag-for-entry is a near-vertical gain — more recall for almost no cost — while every tag-traversal variant costs more for less. **Use tags to find the entry point, not to build edges.**

## Does the smaller surface make the model pick better?

The study's sharpest reversal is on *pick quality*: does a smaller routing surface make the model choose better documents, not just cheaper ones? The intuition says yes — fewer plausible-but-wrong cards means fewer distractors. The first pass couldn't confirm it. With only a lexical (BM25) picker available, the graph surface actually scored *worse* on precision (F1 0.32 vs 0.40), because a bag-of-words picker can't exploit distractor reduction: it doesn't reason over the surface, so a smaller surface just means fewer chances to keyword-match the gold.

For the follow-up, I re-ran it with an actual LLM router, using a deliberately blind protocol: one fresh, isolated agent per (query, surface) pair, each shown *only* its query and one surface's cards, never the gold and never the other surface. Across 12 of the 34 queries (24 agents), the result flips:

| | Flat (A) | Graph (B) |
|---|---:|---:|
| Macro-F1 | 0.541 | **0.587** |
| Micro-F1 (pooled) | 0.454 | **0.593** |
| Pollution (non-gold picked) | 4.92 | **3.67** |

Now the smaller surface produces **at least as good, and on aggregate better** picks, with less pollution — the opposite of the lexical proxy's verdict. The biggest wins came on large, granular-source queries. On one query whose gold was 27 individual source documents, the flat-surface router picked the tidy summary documents and scored **0.0**, while the neighborhood-surface router picked the actual cited sources and scored **0.56** — in the scoped neighborhood those sources *dominate*, so they are the obvious thing to pick.

Caveats:

- **By per-query win count it's a tie** (B wins 3, ties 6, A wins 3). B's aggregate edge is concentrated in a few large-k queries; one of them moves the pooled micro-F1 substantially.
- **Single model, n=12.** The router and the (deterministic) scorer are the same model family; there's no independent evaluator. This is directional evidence, not a controlled trial.
- **Part of B's edge is "right granularity," not purely "fewer distractors."** The benchmark counts granular source documents as gold, and B's neighborhood is denser in exactly those. That's a real retrieval-quality signal, but it's entangled with the neighborhood's composition. I flag it rather than net it out.

Treat the 44–49% context reduction as solid and the precision upside as promising-but-directional.

## Three ways to scope: flat, tiered, graph

Graph-scoping isn't the only escape from O(N). [The previous post](https://kfchou.github.io/llm-wiki-google-okf/) floated a different one, drawn from the llm-wiki comment threads: a **tiered index**. Shard the wiki into subdirectories of "high-level, commonly-used, non-overlapping concepts," give the index a token budget — L0 (~200 tokens, every session), L1 (~1–2K, at session start), L2 (~2–5K, on demand) — and let the agent drill coarse-to-fine. Progressive disclosure by taxonomy instead of one flat scan.

Tiered and graph answer the same question the flat index can't: *which subset of cards is worth scanning for this query?* They differ on where the subset comes from — a taxonomy you impose, or edges already written in the frontmatter.

| | Flat | Tiered (taxonomy) | Graph-scoped |
|---|---|---|---|
| Routing cost / query | O(N) | ~O(√N) | O(neighborhood) |
| Structure comes from | nothing | a curated or learned taxonomy | frontmatter edges (already written) |
| Recall ceiling | 1.0 | topical — high if the page is filed right | 0.81, bounded by frontmatter |
| Page in two topics | seen anyway | one subdirectory home | many typed edges, native |
| Dominant failure | cost | wrong branch at the top tier (silent) | zero-seed entry-resolution miss |
| Standing maintenance | none | rebalance branches, re-learn the ontology | none — reuses provenance edges |

The tiered index has one real advantage graph doesn't: no front door to miss. The agent always starts at L0 and reads down, so a vague query that names no entity still lands somewhere — whereas graph's four complete misses are all *zero-seed*, cases where the resolver caught no entity and traversal never started. A page filed under the right branch is also found by any query that descends into it, edges or not. So the tiered index catches exactly the prose-only gold a frontmatter traversal can't reach.

So why graph? Because "non-overlapping concepts" is the assumption this wiki breaks. The previous post already hedged it: "if no such concepts can be determined at the onset, perhaps an ontology learning procedure can be used." That caveat is the crux: the taxonomy may not exist, and learning it is an expensive, non-deterministic pass you must re-run as the wiki drifts. The frontmatter edges need no such pass; they're already written as `sources:` and `affects_*` for provenance you keep anyway.

**Mega-hubs, and why traversal has to be hub-damped.** Real wikis grow a few pages that nearly everything points at — here, a foundational document of degree ~250. Such a hub breaks naive traversal: fan out *through* it and a single hop pulls in half the wiki, so you are scanning a flat-index-sized surface again and the benefit of scoping is gone. The fix, used throughout the results above, is **hub-damped BFS**: a traversal may *reach* a hub but not *fan out through* it once its degree passes a cap (40 in the recommended configuration). A filesystem tree hits the same hub with no comparable fix. It must either make that foundational document the root — one giant branch, back to flat — or scatter its 250 children under secondary categories, destroying the very relation the edges preserve. The edges keep the hub as a hub; hub-damping just lets a traversal visit it without being swamped.

The budget half of the tiered proposal isn't a rival — it composes. Graph decides which cards are in the neighborhood; an L0/L1/L2 budget can still decide how many of them to load at once. On this mono-thematic wiki the neighborhood is ~half the index, so that second cut is left on the table.

## Limitations

- **The recall gap is real.** ~8% of gold on resolved queries is unreachable via frontmatter edges alone, and the ceiling plateaus around 0.85 even at three hops. The completeness auditor is the intended backstop, but it isn't free and it's propose-only.
- **Entry resolution is deliberately simple** (id + slug-word match, plus surgical tag-for-entry). A better resolver shrinks the miss rate; a vaguer query inflates it.
- **Pick quality rests on a single-model, n=12 run.** The reversal is encouraging but wants an independent-model replication before anyone calls it settled.
- **The scaling win is back-loaded.** Today's wiki is mono-thematic, so the present win is a stable ~2×. The 74–90% projection depends on the wiki diversifying into edge-separable topics — a stated assumption the current wiki can't yet confirm empirically.
- **Gold = declared `sources:`.** The benchmark measures retrieval against *recorded* dependencies. If an analysis silently leaned on a document it never cited, neither method is credited or penalized. That's a benchmark-definition choice, not a bug.

## How to adopt it

If you're routing LLM queries over a flat whole-wiki index — an llm-wiki or a [wiki-skills](https://kfchou.github.io/wiki-skills/) vault past a few hundred pages — you're paying O(N) on every query for an answer that lives in O(neighborhood). The scale fix people reach for first is a vector database; you don't need one. Your pages already carry structured relationships in frontmatter, and a graph-scoped index turns that routing bill from linear-in-wiki into bounded-by-topic while staying in plain markdown. The practical recipe, in the order the evidence supports:

1. **Extract the graph from frontmatter** and route over the query's 2-hop, hub-damped neighborhood. Spend most of your implementation effort on reference resolution: your pointers won't be perfectly consistent — the same document gets named different ways on different pages — so resolve defensively, canonical id first, then the looser forms. It is the highest-value and easiest-to-botch part of the build, so test it explicitly.
2. **Keep a flat-scan fallback.** When entry resolution returns nothing, fall back to the full index. This caps the downside: the graph method is then never worse than flat, only sometimes equal.
3. **Add surgical tag-for-entry** ahead of the fallback — tags to find the entry point, skipping mega-tags. It closes the entire entry-resolution failure mode for ~9% more context and makes the expensive fallback fire far less often. Do *not* add tag traversal edges; they rebuild the mega-hub.
4. **Run a completeness auditor** as the recall backstop for the frontmatter-only gap — a propose-only pass that surfaces prose-only dependencies as candidate structured edges for a human to accept.

The whole thing is additive and reversible, and it never leaves markdown: the graph selects which cards the model scans, the cards themselves are unchanged, and a feature flag reverts to flat instantly — no embeddings, no external store. The context reduction is solid (~44–49%), the precision upside is promising-but-directional, and the recall cost is bounded and measurable.
