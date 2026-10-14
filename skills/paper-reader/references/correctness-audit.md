# Check the paper, not just the report

The paper is evidence about what its authors wrote and measured, not an authority on whether every statement is true. Citation, peer review, successful code execution and valid LaTeX are not correctness checks. Use this audit for the entire supplied paper and available supplements, independently of the coverage audit and the report-only reader pass.

When knowledge-curator reuses this audit, the audited scope is the tutorial and its source dependencies, and the presentation differs: teach only verified, corrected content. Store source errors, original formulas, diagnosis, correction justification and rechecks in its ledger. Replace an uncertain result with a checked formulation/source or omit optional material; an unresolved central result cannot be published as taught knowledge. Do not reproduce source-error panels in tutorials. The instructions below to show original errors and their impact apply to critical paper reports, whose purpose includes evaluating that particular paper. Valid counterexamples explaining a concept's conditions are appropriate in either document.

## Inventory every scientific item

Traverse the abstract, main text, displayed and inline mathematics, algorithms, figures/captions, tables/footnotes, conclusion and available supplements. Record every scientific claim, formula, inference and conclusion, including background claims and minor results. Split compound claims when their evidence or truth conditions differ. Repeated statements may share an entry with all their locators; identify assumptions and definitions without misrepresenting them as proved results. Bibliographic entries do not each require a scientific verdict.

Give equations without numbers a page, paragraph and short literal locator. Visually check the original PDF when extraction could have changed a sign, index, exponent, bound or symbol. Inventory before judging: a plausible summary of the main result cannot establish that all items were inspected. Prioritize dependencies, but do not silently omit the rest.

Maintain a working ledger under `data/reviews/`. For each item record:

- `id`, `kind` (claim, equation, proof_step, algorithm, empirical_result, conclusion, definition or assumption), source version and exact locator;
- the original statement/formula, its scope, symbols and hypotheses;
- cited evidence, dependencies on other ledger items, and checks actually performed;
- derivation, calculation, counterexample or source comparison supporting the assessment; retain scripts/inputs/results when used;
- `status`: `supported`, `error`, `unsupported_scope`, `ambiguous`, `inconsistent`, or `unverified`, with a concrete rationale;
- impact on downstream arguments and a report section/issue anchor when readers need the finding.

`supported` means supported within the checked conditions, not universally true. For definitions/assumptions it means the stated role is explicit and internally coherent, not that an empirical assumption has been proved. Missing data, inaccessible supplements, unavailable experimental code or checks beyond the agent's ability remain `unverified`, with the missing evidence and affected claims named. An unchecked item is never silently passed. Do not announce an exhaustive audit while ledger items or source regions remain unexamined.

## Check equations and their use

For every formula, reconstruct its inputs and conclusion before accepting it:

1. Resolve symbols, shapes, units, domains, indices, summation ranges, normalization, boundary conditions and exceptional cases such as zero denominators. Compare definitions across prose, equations and algorithms.
2. Derive asserted equalities, inequalities, gradients, probabilities and complexity bounds from the stated assumptions. Check signs, missing factors, dependence between random variables, conditioning and the legitimacy of exchanging expectations, limits, derivatives, maxima or integrals. Check that cited theorems apply to these objects and hypotheses.
3. Separate definitions and approximations from identities. A surrogate, relaxation, bound or asymptotic rate must not silently become an equivalent objective, finite-sample guarantee or exact solution. Trace a local defect into later conclusions instead of checking formulas in isolation.
4. Use valid boundary cases and small counterexamples; use numerical/symbolic tools where they clarify the issue. Finding no numerical failure is not a proof. Counterexamples must satisfy the paper's hypotheses. Do not infer mathematical error from floating-point rounding or OCR corruption.
5. Where a correction is justified, show the original, the failed step, and the corrected expression with assumptions. Mark your reconstruction as analysis. Do not silently repair the paper or attribute a guessed intended formula to the authors.

## Check assertions, measurements and conclusions

For every non-formula claim, identify its evidence and the strongest scope that evidence supports. Recompute derived quantities where data are available: averages, percentage versus percentage-point gains, sample totals, metric directions, units, speedups and table-to-text comparisons. Account for macro/micro averaging, denominators, rounding and aggregation before declaring a mismatch.

Check dataset splits, controls, baselines, compute budgets, uncertainty, ablations and contrary outcomes against the conclusion. Correlation or one ablation does not automatically identify a causal mechanism; success on evaluated datasets does not prove all-domain superiority. Inspect primary cited sources for background assertions and theorem dependencies when needed. Check relevant paper/code discrepancies without assuming a current branch is the exact experimental revision. Reading a table verifies a reported value, not reproducibility of its experiment.

Distinguish these judgments in prose:

- **Confirmed error:** establish an exact contradiction, invalid step or valid counterexample. State it clearly, show decisive evidence and affected conclusions.
- **Unsupported scope:** evidence supports a narrower claim. Give that conclusion; do not call a measurement false because its interpretation is too broad.
- **Ambiguity/inconsistency:** notation, wording, source versions or implementations admit conflicting readings. Show readings and consequences without guessing an error verdict.
- **Unverified:** evidence or analysis is insufficient. Say what remains unchecked and why; neither endorse nor condemn it.

Before labeling an error, reread local definitions and the original page, attempt the most charitable interpretation allowed by the text, and independently recalculate the decisive step using a second approach where practical. Do not claim independent human/agent review unless it occurred. The goal is accuracy, not a quota of faults.

## Put findings where they matter

Immediately after the affected formula or argument, give a visible, labeled note with the source location, original assertion, diagnosis, decisive derivation/example, and impact. Do not hide a serious error entirely behind a collapsed control. Longer supporting calculations may be expandable after the visible diagnosis. Use semantic note styles from `CONTENT_SCHEMA.md`; color supplements the written label.

Include a concise findings overview when multiple issues affect the paper. Distinguish local writing defects from defects in a central proof, method or empirical conclusion. Explain what remains supported; one proof error does not itself refute an independently reported experiment. Avoid generic caveats or an unqualified verdict on the whole paper.

Keep all item-level analyses in the ledger, while exposing material errors, uncertainties and effects in the report. Report omissions for readability do not exempt source items from audit. If incomplete, disclose the specific unverified scope in the report's coverage note and delivery message. Never relabel older reports as fully checked just because the skill was updated.
