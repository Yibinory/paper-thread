---
name: knowledge-curator
description: 检索概念的原始工作与权威资料，编写面向零基础读者的详细知识教程，贯通原理、推导、应用与变体；审核来源、正确性、理解与知识链接，并维护概念身份和稳定引用。
---

# Knowledge Curator

Locate the PaperThread project root containing both `paper.py` and `CONTENT_SCHEMA.md`: first inspect the current workspace and its ancestors, then the resolved skill path and its ancestors. Do not assume this skill is a symlink or that a user-level installation contains the application. If no project is available, ask for its location. Run commands from that root with Python 3.10+: `python3` on macOS/Linux, `py -3` or `python` on Windows, or the project virtual environment (`.venv/bin/python` / `.venv/Scripts/python.exe`). The examples below use `python3`; substitute the available interpreter. Read and write content files as UTF-8. Read the schema. The agent reasons about identity and writes explanations; the tool provides structured memory and revision-safe storage.

## Identify meaning before names

Read `inventory --kind concept` and follow `next_offset` when present. A small collection can be scanned as compact definition cards. For a large collection, inspect relevant and adjacent domains using `--domain`, and search alternate Chinese/English names. `search QUERY --context CONTEXT --kind concept` offers lexical candidates; it cannot decide semantic equivalence or prove absence. Read candidate bodies using `get ID` before reusing, extending or merging.

Compare definitions, objects, assumptions, abstraction level and intended use. Decide and briefly record the closest existing ID and why it is adequate or insufficient. Different names can identify one concept; the same abbreviation can identify several. Parent concepts and special cases are related, not synonymous. Preserve informative distinctions in `not_this`; functional phrases belong in `semantic_terms`, not automatically in aliases.

Reuse an adequate page. Extend an existing page if the missing part belongs to the same concept, preserving meaningful anchors. Create a new stable ID only for a distinct reusable idea needed in the current reading. Paper-specific design reasons and new contributions stay in the report. Stable IDs do not change when titles do.

## Research the concept independently of the triggering paper

For a new page or substantive rewrite, read [source research](references/source-research.md) and actively search for the original work introducing the concept, authoritative developments and pertinent variants. The supplied paper identifies a use of the concept; it is not the default source of that concept. Verify attribution and read the relevant source passages, not just abstracts or search snippets. For established concepts with several historical contributors, describe the lineage without inventing a single origin. Record exactly what was read and unresolved source access.

## Write a detailed tutorial for a first-time learner

Read [tutorial writing](references/tutorial-writing.md). The knowledge page is a reusable, self-contained learning resource, not a short appendix sized to the triggering report. Prefer depth: develop the problem, intuition, mathematical objects, derivations, fully worked examples, practical use, failure cases and meaningful variants. Do not compress away reasoning to meet a length target. Organize substantial content into clearly named, stable sections so experienced readers can enter where they need it. A glossary, formula collection or list of variant names does not meet this requirement.

Introduce knowledge links at the point where a dependency does work. Explain its local meaning and why it is needed, then link to the exact adequate section. Apply the [iterative dependency workflow](references/tutorial-writing.md#resolve-dependencies-iteratively) whenever research, drafting or review reveals a substantial missing foundation: inspect existing pages, reuse or improve them, or create a separately researched and reviewed tutorial. Apply the same process to dependencies discovered in that tutorial, then return to the referring passage and check that the explanation now works. Do not stop at one level or leave a promised link to an unwritten page. Define small prerequisites inline, keep the current concept's own reasoning here, and distinguish required foundations from optional related reading.

## Review the knowledge before publication

Apply the separate gates in [knowledge review](references/knowledge-review.md): source/attribution coverage, item-level mathematical and factual correctness, first-time-reader reconstruction, application/variant transfer, and links/rendering. Build a concept reading pack with `review-pack k-ID --draft .local/drafts/CONCEPT.json --to .local/review-packs/k-ID`. Keep this source-free comprehension pass separate from the source audit. Use an independent reader only when available and authorized; otherwise record `same_context_knowledge_only`, never a fictional blind test.

A cited original work, textbook or existing knowledge page can be wrong. Independently derive, recompute and inspect conditions using the paper-reader [correctness audit](../paper-reader/references/correctness-audit.md). Its knowledge-tutorial presentation rule applies: teach only the corrected, justified result and derivation; keep erroneous source statements, diagnosis and correction provenance in the audit record, not in teaching panels. If a repair cannot be justified, find an independently checked source or remove the unsupported optional result; do not teach an unresolved central result. This is correction, not concealment of an unchecked error. Keep concrete question → repair → recheck records, source locators, evidence and the final draft digest under `data/reviews/`. Do not imply that any textbook is entirely error-free or that auditing this tutorial verifies all its sources.

## Save and preserve references

When an intermediate calculation or changing condition is hard to see in prose, apply the paper-reader [interaction guide](../paper-reader/references/interaction-design.md). Keep the full conceptual explanation available as text and put paper-specific measurements and variant choices in the report. Interactive configurations travel with the knowledge revision and must be included in review packs.

Use `get ID` to obtain the current revision, then `save FILE --expected-revision REV`; new pages use `save FILE`. `alias ID NAME --expected-revision REV` adds a verified name. Run `check` and `build`; no embedding model or index rebuild is involved. Keep notes and reader state separate.

For a duplicate merge, reconcile bodies and anchors first and inspect backlinks/prerequisites, then use `merge SOURCE TARGET --expected-source REV1 --expected-target REV2`. The old ID redirects and historical snapshots survive. Scores do not authorize merging.

Reports retain the knowledge versions they cited. If the task intentionally updates a report to improved knowledge, inspect the relevant changes before updating its pins. Do not refresh unrelated reports by default. Return ID, section, revision, and the tool-returned URL, with any unresolved ambiguity. Visits and silence never imply mastery.
