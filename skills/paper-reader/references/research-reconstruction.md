# Explain the decisions behind the result

Use this alongside the argument map, before drafting. It adds research reasoning to the connected explanation, not a second questionnaire or compulsory block after every mechanism. The design draws on [Paper X-Ray](https://github.com/Wang-auspicious/paper-xray), while retaining PaperThread's beginner knowledge links and separate correctness audit.

## Reconstruct a defensible choice, not a fictional history

For decisions carrying the contribution, find the concrete observation, prior result or available tool that makes the proposal worth trying. Locate the authors' stated motivation and compare it with what their method actually changes. Explain a fair simple alternative on the same input. Identify its relevant limit or cost without claiming every prior method must fail.

Build a decision chain: available evidence → plausible intervention → predicted observable change → test distinguishing it from an alternative explanation. A thought experiment can clarify a mechanism, but cannot establish discovery order or experimental success. Do not invent failed first implementations, reviewer requests, hidden motives or tuning histories. An unexplained choice can remain unexplained.

Wording such as “prove,” “observe,” and “possibly” identifies the claimed scope; it is not evidence about confidence, honesty or private thoughts. Compare that scope with the proof or measurement. Code is evidence about a particular implementation, not automatically the experiment used for the paper; record its revision and reconcile discrepancies.

Keep provenance and correctness separate. At substantive reconstructions use the visible labels and semantic styles in the schema:

- **【文中有据】**: an attributed author statement or observation with a precise locator. This does not mean independently verified or correct.
- **【推断】**: analysis supported by specified premises. State the reasoning and what would change the conclusion. Direct calculations can say “按所列假设计算” rather than pretending they were measured.
- **【猜测】**: a useful but weakly supported possibility, with a discriminating check. Omit speculation that only adds a story; speculation is not a quota.

Label the relevant assertion or coherent paragraph, not every ordinary definition. Separate author testimony and analysis within mixed passages. A constructed numerical example additionally says **教学算例** and lists its simplifications. These labels are neither probabilities nor a replacement for error/scope findings. Error findings still require decisive evidence.

## Make implementation choices intelligible

For consequential mechanisms, explain what a reasonable simpler implementation would do differently. Where informative, develop a specific failure symptom and affected quantity, a small diagnostic distinguishing plausible causes, what its possible outcomes imply, and a repair with its cost or new failure. Present this as a proposed diagnostic unless documented or actually run. Place it after the mechanism that makes it intelligible; do not mechanically add a block everywhere.

Connect important hyperparameters to competing quantities, units and observable behavior. Explain why small/large settings could matter, whether the paper tested this, and how the value was selected. A parameter is not necessarily a “patch”; do not invent its purpose. Do not transfer a toy example's weight to the paper's differently scaled representation. Missing selection protocols, equal-budget controls or uncertainty remain visible where they affect the conclusion.

## Calculate the mechanism on a small object

Carry a coherent example through input → changed object → intermediate calculation → decision/update → resulting use. A table of invented final losses alone does not show how the method obtains them. Compare the simpler alternative at the point of divergence, holding conditions equal where possible. Distinguish this teaching contrast from an empirical baseline result.

Before a central formula, establish its purpose and define each symbol's type/shape, meaning, units and whether it is fixed or updated. Show an important intermediate step with explicit values, then the result. An optimizer may need the gradient sign and first updates; a systems method a complete request; a proof a finite example satisfying its assumptions. Hand calculations, scripts and interactive views must agree. State what the example cannot establish when returning to real data.

Link reusable foundations to detailed knowledge tutorials at their point of use. Keep the paper-specific substitution, decision and consequence in the report. Do not move the mechanism's numerical explanation behind a prerequisite link or repeat a whole textbook lesson in the report.

## Assess what the evidence can decide

Separate overall performance, the proposed mechanism and a stronger theoretical interpretation. An accuracy gain may support the first without isolating the second or proving the third. Check the decisive intervention, constants, baseline tuning, data/model selection and measurement uncertainty.

Recalculate means and gains allowing for rounding; name percentage points. Identify what “±” denotes, sample/seed count and missing baseline variance. A difference comparable to variability merits caution but is not a significance test; overlapping error bars alone neither prove equivalence nor refute a difference. Never fabricate intervals from an unexplained “±”.

Suggest a concrete next check: what observation would support the proposed explanation, and what would favor another? Keep tested results and suggested experiments distinct. A proof error does not erase a reported measurement; an impressive measurement does not repair a proof.
