# Source coverage

This audit consults the source to check what the report explains, not whether the paper is correct. Perform the separate [correctness audit](correctness-audit.md) for every claim, formula, inference and conclusion. The report-only reader review remains separate and must not use the paper to supply missing explanations.

## Establish the source inventory first

Record the supplied version, page numbering and which supplements/code were actually read. Traverse sections, figures, tables and available appendix headings. Inventory substantive points: task and constraints; representative prior mechanisms; each proposed component and its role; assumptions and central theoretical results; experimental setup; each research question, main result and material exception; ablations, sensitivity, cost and applications; limitations and appendix results that change interpretation. Bibliography entries and repeated wording do not each need report paragraphs.

Give each unit a source locator and importance. Use the inventory to check completeness, not to dictate the reading order or assign one main section per unit. Several source units may answer one reader question; a detailed proof may be attached to the claim it qualifies. Preserve central reasoning and consequential exceptions. Do not infer completeness from heading counts or keyword matches. A section can contain several claims with different evidence. Unavailable material remains unverified; it cannot be marked covered.

## Compare meaning in both directions

For every unit record: source point → report section/short supporting passage → coverage decision and rationale. Use `explained`, `brief` (why enough), `linked` (which reachable explanation), `omitted` (what and why), or `unverified` (missing source). A mention with no mechanism/evidence is a gap when the point is central. Cross-check report → source for unsupported facts, invented connections and empirical numbers in interactions.

Resolve missing contributions, missing steps, changed experimental conditions, unexplained headline claims and omitted contrary evidence before publication. Peripheral proofs, implementation grids and repetitive examples may be summarized or omitted with precise reasons. Publish a compact coverage note describing actual scope and omissions; keep the detailed matrix in `data/reviews/`. Avoid percentage scores that treat all points equally or present author self-review as a guarantee that every point was captured.

## Connect coverage to correctness

Link source units to the correctness ledger. Include all scientific claims and conclusions, not just the abstract or main contributions. For each, identify:

1. The author's proposition and intended scope, with a source locator.
2. Its nature: mathematical statement, empirical comparison, mechanistic hypothesis, efficiency argument or generalization beyond tested conditions.
3. Supporting proof/experiment and the relevant baseline, metric, dataset and controls.
4. Assumptions, competing explanations, exceptions and contradictory evidence. Assess whether the experiment separates the proposed cause from other changed factors.
5. The strongest conclusion justified by that evidence, distinguished from the author's wording and the report author's analysis.

Explain significant judgments in the report where the evidence is read, optionally followed by a compact claim/evidence table. Do not append generic caveats to every row. No invented confidence percentages or automatic verdict based on metric gains. If a proof step or paper/code mismatch remains unresolved, give the concrete issue and what it does and does not undermine.

## Keep the record honest

Save inventory/matrix, links to item-level correctness analyses, actual material consulted, findings and repairs, omissions, and final draft digest. Mark review mode `author_source_comparison` unless an independent comparison really occurred. Coverage may be complete while correctness remains unverified; report those separately. Do not carry a pass across a changed draft. Source audit can expose new reader gaps; reread those sections under the reader-review evidence boundary after repair.
