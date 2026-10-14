# Teach the principle and how to use it

The reader may be meeting the field for the first time. The page should let them explain why the concept exists, follow its reasoning, work a small case and recognize when it applies. Detail belongs here so reports can remain focused. There is no word quota or fixed section count; length is justified by the missing reasoning it supplies.

## Build one continuous explanation

Start with a concrete problem and an understandable baseline whose limitation motivates the concept. Explain the intended input, output and success criterion. Develop the intuition into a precise object or operation: distinguish an analogy from the actual model. Define notation, units, domains and assumptions before relying on them. Explain mathematical vocabulary locally when that is sufficient.

For a central formula, show what each term measures, why it is present, and how the expression follows from the preceding setup. Spell out nontrivial transformations and the assumptions they use. Distinguish definitions, identities, proved claims, approximations and heuristics. Explain boundary/degenerate cases when they change interpretation. A difficult general proof may be optional, but give an honest finite or special-case derivation and state exactly what remains a cited theorem. Do not put the only explanation of the core mechanism inside a collapsed panel.

Carry a worked example from input through intermediate states/calculations to an interpreted output. Choose values that expose the mechanism, not just convenient zero/one answers. If optimality, unbiasedness or another property matters, show why it holds rather than merely producing a feasible result. Then use a contrasting case or failure example to show why the assumptions matter. Label constructed data and keep arithmetic reproducible.

Teach the verified formulation directly. Do not reproduce a source's erroneous formula, attach a source-error panel or ask a beginner to distinguish an erroneous version from its correction. Establish the corrected result from a derivation and/or an independently checked authoritative passage, with honest attribution; keep the original defect and repair in the audit record. Valid counterexamples and explanations of misapplication remain useful when they teach the correct conditions. They are different from an errata tour of the sources.

## Continue from theory to application

An application should state the task, how real observations become the mathematical inputs, what is optimized/computed, how a user interprets the output, and what decisions/parameters affect it. Work through a practical small case or an executable/pseudocode procedure when that explains implementation. Clarify training versus inference, exact versus approximate computation and units or normalization where relevant. Do not reduce application to “used in image generation, retrieval and optimization.”

Cover variants that a reader is likely to encounter or that resolve the concept's central limitations. For each selected variant, explain the changed assumption/objective/representation, the need it addresses, the retained and lost guarantees, a concrete consequence and its source. A comparison table can orient the reader, but cannot replace the mechanism. Extend a variant in a separate linked page when it has its own substantial reusable explanation; do not turn the parent into an unexplained name list. Do not manufacture a variant section for a concept with no relevant variants.

Explain meaningful connections and common misapplications through examples. Keep the triggering paper's specific implementation choices in its report. A general tutorial may briefly locate that use, but must remain intelligible and useful without knowing the paper's title or notation.

## Let links carry depth without breaking the argument

At the first substantive use of a prerequisite in each section, supply its immediate role and a link to the exact section answering the reader's likely question. A basic definition or one-line arithmetic step can stay inline. Create/extend a separate page for a substantial reusable dependency only after checking conceptual identity against the inventory. The target must explain enough for this use, not just share a keyword.

Write headings that expose the reasoning and preserve useful anchors. Break long derivations into explanation, equations and worked tables; use the shared semantic colors and notes. Optional advanced proofs can use `details`, but the beginner's mainline stays visible. No upfront prerequisite catalogue or artificial learning levels that require clicking to reveal ordinary prose. An interaction is optional and must improve a specific understanding task over a static presentation.

Required foundations form an acyclic dependency chain. Optional application links may lead back to a parent concept; label their role in prose and make neither page require that round trip to explain itself. Review the route as a beginner: “I do not know this term → linked explanation → I can now perform the next step.” An older short entry is not adequate automatically because it already exists.

## Resolve dependencies iteratively

Discover dependencies while researching, writing and reviewing, not only in an initial outline. When a reader needs another concept to follow a step, decide whether a local explanation suffices or a separate tutorial is warranted. Split a substantial reusable idea whose explanation would interrupt the current concept's development. Keep simple definitions and the current concept's own central reasoning inline; a page should not become a collection of links. An optional deeper variant can also merit a separate page, but distinguish it from a prerequisite.

Track unresolved dependencies in the working review notes: referring passage, the specific understanding needed, closest existing concept/section, decision to reuse/extend/create, and remaining work. Compare meaning and scope through the inventory before assigning an ID. Combine requests for the same concept even when several pages or aliases lead to it.

For each missing or inadequate dependency, research and write it using this skill's full tutorial and review process. If it introduces another substantial missing dependency, process that in turn. For example, A → B → C means C must become usable, then B must be checked with C, then A with B. Reuse an adequate reviewed C instead of generating it again. Newly discovered needs reopen the relevant work; neither finishing A's prose nor creating B's file ends the process.

Stop expanding a branch when the reader can obtain the understanding needed at its point of use from an adequate existing tutorial or a sufficient local explanation. Do not stop just because a preset depth or page count has been reached, and do not expand every mentioned term, citation or neighboring topic into an encyclopedia. Each new page must have an actual explanatory role and satisfy the normal tutorial standard.

Check for cycles by meaning as well as IDs. If A requires B for its first explanation and B requires A, reorganize the foundations: supply an independent local definition, factor out a shared prerequisite or split the scopes. Do not merely relabel a necessary dependency as optional to bypass a cycle check. Record actual required concept IDs in `prerequisites`; optional application links stay out of that field. The tool checks declared cycles, while the agent must find circular explanations in the prose.

Keep incomplete pages and provisional links in drafts. Review and save ready prerequisites before pages that need them; do not publish placeholders to make a link resolve. Delay optional links to unpublished parent pages until their targets exist. After a dependency is completed or revised, return to every affected referring passage in this task, align its terminology and assumptions, and verify that a reader can now perform the next step. Keep the local reason for using the dependency in the parent page. A blocked core dependency leaves the dependent draft unfinished; an optional branch may be deferred with an honest scope note. Retest the reachable reading path using the revisions actually reviewed.
