# Review a knowledge tutorial before publishing it

Use these gates for new pages and substantive rewrites. Record actual evidence, not completion ticks or a numerical quality score. Technical validity cannot prove learnability; learnability cannot prove correctness.

## 1. Sources, attribution and teaching coverage

Compare the draft with the source-to-explanation map. Check that the original/foundational work and each explained variant have been sought, the relevant passages were read, and citations support the nearby claim. Identify any reliance on a triggering application paper or unverified secondary attribution. Inspect whether a beginner has the motivating problem, object/notation, reasoning, worked example, practical application, assumptions/limits and pertinent variants. Use justified `not_applicable` or a scoped source limit where appropriate, not empty template sections. Coverage concerns this concept's learning goals; it is not a claim to summarize every source paper in full.

## 2. Item-level correctness

Inventory every scientific claim, definition, formula, inference and conclusion in the tutorial. Apply the linked paper-reader correctness audit to those items and their actual source dependencies. Check signs, units, dimensions, normalization, domains and theorem hypotheses. Independently recompute each constructed example and confirm the explanation matches the calculation. Challenge at least the central mechanism with meaningful boundary or counterexamples when applicable. Numerically sampled success is not a proof.

Distinguish an original source's error from a tutorial transcription or interpretation error in the ledger. For each defect, retain the exact source, diagnosis, justified correction or replacement source, dependent explanations, recomputation and final-page location. The teaching page presents only the corrected result, its conditions and useful derivation; exclude original incorrect expressions, source-error panels and errata in citation titles. Do not satisfy this check by deleting a warning while leaving an unsupported formula or dependent example. If correction is uncertain, research a sound alternative or omit the optional claim; a central unresolved result blocks readiness. The tutorial's ledger does not certify unchecked statements elsewhere in its sources.

## 3. Read using only the tutorial and its links

Generate a pack:

```sh
python3 paper.py review-pack k-ID --draft .local/drafts/CONCEPT.json --to .local/review-packs/k-ID
```

The reviewer receives `concept.json`, `knowledge.json`, figures and neutral instructions, with no source full text, author notes, desired answers or prior findings. When independent delegation is available and authorized, use a fresh context. Otherwise explicitly record `same_context_knowledge_only`; same-context self-review is not a blind test. The reviewer must point to written evidence rather than fill gaps from memory.

Read in order. For each comprehension break record section, short exact quotation, concrete question, what has already been established, whether a link resolves it, and severity. Check undefined terms, omitted algebra, motivation leaps, ungrounded analogies, inaccessible prerequisites and a dependency introduced only after it is used. The question “why is this useful?” needs an actual task and consequence, not another adjective.

## 4. Reconstruct and transfer

Using only the pack, explain the problem and mechanism in ordinary language; reconstruct the central derivation with its conditions; work the example from inputs to output; then change an input or assumption and predict what changes. For an application, explain how data become inputs and how the output informs a decision. For a variant, state exactly what changes and one situation favoring or ruling it out. Give supporting section locations for each nontrivial step. Failed reconstruction becomes a specific repair request, not a score.

Inspect a representative report-to-knowledge jump when the page is used by a report. Verify that the target section answers the question motivating the jump and that the report retains its own reasoning. Exercise nested knowledge links and the return route. Required concepts must not refer the reader to each other for their first definition.

Follow unfamiliar required foundations as far as the explanation needs, rather than stopping after one link. Record what the reader needed before leaving, what the target actually teaches and whether the reader can complete the original step after returning. A page existing, loading or sharing a term is insufficient. Missing or shallow dependencies become reuse/extension/creation work in the tutorial guide's iterative workflow; newly created pages receive their own source, correctness and comprehension reviews. Do not let a parent page's review stand in for those reviews.

## 5. Repair, render and release

Repair the first missing dependency and reread the affected reasoning and application, rather than appending an FAQ. Return to sources where necessary. Keep `question → evidence/repair → recheck result/locator` records. Recompute changed examples. Check formulas, stable section anchors, nested links, full-page and drawer reading, narrow-screen tables and the shared color hierarchy. Check meaningful interaction states only if present.

Before release, reconcile the working dependency notes: every required gap is resolved by an adequate reviewed page or inline explanation, and affected parent passages have been rechecked after the dependency changed. No missing targets, placeholder tutorials or circular foundational explanations may carry a core step. List deliberately deferred optional expansions separately. A syntax/link check cannot establish that this dependency work is complete.

Record final draft digest, exact revisions of reachable knowledge, source inventory, correctness ledger, actual reader-review mode, findings/resolutions and remaining limits under `data/reviews/`. Do not claim a gate passed simply because a file was generated. Do not publish a ready page with an unresolved core misconception, unsupported central result or unusable main example. Clearly scoped optional gaps can remain visible. Save the reviewed page to its existing ID; update only report pins whose changed knowledge has been reviewed for that use. Source, comprehension and technical checks are separate and all must describe the version actually published.
