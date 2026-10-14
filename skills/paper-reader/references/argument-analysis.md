# Reconstruct and test the paper's argument

Read this before outlining or regenerating a report. Reconstruct the scientific argument, then design how an unfamiliar reader can acquire it. These are different tasks: a collection of accurate contribution analyses can still produce a fragmented report.

## Separate setting from the research gap

Establish the ordinary task and why a reasonable existing procedure encounters a concrete difficulty. Explain that mechanism before naming its research setting. A setting specifies information and constraints; it does not itself explain why this method is needed. A paper may address a neglected opportunity or a cost tradeoff rather than an impossibility in prior work. Do not invent failure to fit a template.

Identify the specific question within that setting. Read the introduction, method, discussion and conclusion together; contrast the authors' emphasis with the actual changed component. If the motivation could introduce nearly any paper in the field without changing a word, the research gap is still missing.

Before prose, save a compact argument map under `data/reviews/`. For each central contribution record:

- task/information and specific unresolved obstacle or opportunity;
- a representative earlier mechanism, its actual strengths and relevant limitation;
- the proposed change and intermediate mechanism by which it might help;
- assumptions, cost/tradeoff and alternative explanations of the reported gain;
- the observation, derivation or controlled comparison that would distinguish explanations, and what evidence the paper actually supplies;
- source locators and status: author motivation, established result, empirical observation or report-author inference.

This is a reasoning aid, not a mandatory published questionnaire or row quota. Search and read decisive baseline sections. Do not equate “learned from source data” with “cannot generate novelty,” a limited visualization with an impossibility result, or authors' criticism of a baseline with an independently established fact.

## Design the whole explanation before its sections

Add a reading path to the same argument record before choosing headings. Write a short continuous explanation that connects the concrete difficulty, the paper's chosen intervention, the complete proposed solution and the evidence-qualified answer. Use the actual objects and changes in this paper. A heading list, “background → method → experiment” outline, contribution cards, or a sequence of announced questions is not this explanation. If the connected account needs an unstated premise, settle that premise before expanding prose.

Pay particular attention to the move from problem to approach. A failure does not select a remedy by itself. Explain what information, computation or constraint is missing, what the proposed intervention supplies, and how that could change the failure mechanism. Give enough context to see why the authors investigate this route among feasible ones; do not survey every alternative or claim the chosen route is logically inevitable. Separate a useful teaching reconstruction from the authors' actual motivation and from a result established by evidence. A shared example can expose this change: show what the old procedure cannot distinguish, what new operation or observation becomes available, and what it lets the learner or system do differently. Merely reusing the same example's name is not continuity.

Check that the reader can understand the approach as a whole before meeting subordinate machinery. For a method, give the minimum meaningful account of input, intervention, resulting object, how it is used and eventual output. A label-only pipeline is insufficient. Later detail should resolve a known uncertainty in that account. For theoretical, empirical or systems papers, choose the corresponding whole account—such as the proposition and its proof idea, the phenomenon and competing explanations, or the end-to-end bottleneck and proposed change—without forcing an algorithm template.

Derive sections from this account. For each planned block, record briefly:

- what the reader can already explain, backed by earlier content rather than future sections;
- what unresolved issue this block addresses and how it serves the paper's central inquiry;
- the new understanding it establishes and where that understanding will be used.

These are content dependencies, not sentences to append to section boundaries. They may require a different order, merging nominally separate topics, or moving detail out of the main reading path. Keep just enough baseline explanation before a decision to make the choice intelligible; place fuller comparisons where their distinctions can be used. Do not announce a preferred answer and then use a detached related-work catalog to supply its missing rationale.

Some material forms parallel branches rather than a single chain. Group those branches under the question they jointly answer, make their common purpose clear, and return with an updated answer. Do not manufacture a causal transition between independent experiments. Order is allowed to be flexible among genuinely parallel units; the problem is material with no established purpose or prerequisites.

Plan detail and evidence around the inquiry. A parameter distribution, implementation optimization or proof subcase earns its position by what it helps the reader understand now. Coverage does not require every source item to become an equal-weight main section. Group experiments by the hypotheses they test and the boundaries they establish, not simply by table/figure order or “main” versus “additional” results. Decide whether theory supplies a design reason, a correctness requirement or a stronger interpretation to audit, and establish that role before its technical treatment. Keep consequential errors and their impact visible where a claim is used; extended verification may sit in an attached subsection so it does not start an unrelated second report. Do not defer a prerequisite, central contribution or adverse result needed for the main conclusion.

## Follow a design through to its consequence

Explain what each central choice changes in an actual object/computation. Follow it through the objective, optimization, representation and final use. Keep the task objective, tractable surrogate, implemented update and measured outcome distinct; shared notation does not establish equivalence.

Inspect the inferential bridges that matter here, such as “higher loss → useful variation,” “larger distribution change → target coverage,” “tighter bound → faster search,” or “invertible dynamics → valid individual counterfactual.” Explain the intervening conditions, how the method addresses them and what evidence is missing. Merely appending “not guaranteed” does not explain the bridge.

Use counterfactual design reasoning when helpful: what changes if the new component is removed, randomized or replaced by a simpler existing one? Connect to actual ablations. If several components change together, distinguish the measured system benefit from attribution to one component. A proposed missing experiment is analysis, never an experiment the authors performed.

Depth may reveal an unsupported explanation rather than a hidden justification. Say precisely when evidence cannot distinguish mechanisms, instead of supplying a plausible story as fact. Evaluate the strongest fair version of an argument before criticizing it.

## Check the architecture as well as each section

After drafting, reconstruct the whole account using only passages already available to a reader at each point. Apply the procedure in [reader review](reader-review.md). Do not look at a later heading and invent the question that supposedly made it necessary. A statement such as “we can generate new data” may name the next topic while still failing to explain how that intervention addresses the preceding difficulty.

Then check each section's premises, reasoning and conclusion within that account. Verify that details develop an established whole, comparisons inform a decision, evidence revises the hypotheses actually introduced, and the ending resolves the initial inquiry at the supported strength. Diagnose orphaned details, repeatedly restarted motivations and technical branches that never return to the central question. A local statement can be correct and still be misplaced.

Record the structural diagnosis and changed organization, not only edited transition sentences. If the whole account fails, reopen the outline before polishing paragraphs. Reread the revised mainline, including what moved material now presupposes. Reusable theory can be linked, but this paper's explanatory steps belong in the report. No fixed section/check/review count establishes depth or coherence.

The source audit checks that this argument fairly represents the paper. The report-only reader pass separately checks that it is actually written down. An accurate private map cannot rescue a report whose reader still has to infer its organizing logic.
