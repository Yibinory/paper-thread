# Reader review before publication

The purpose is to find what an author who knows the paper has silently supplied. This is a comprehension check, separate from source accuracy checks and HTML/formula validation.

## Keep the evidence boundary honest

A genuinely independent reader receives only the report, its reachable knowledge pages and figures. Do not send the original paper, the author's outline, suspected mistakes, prior reviews or the intended explanation. Use a fresh context when independent agent work is available and authorized. The reviewer can understand ordinary language and use knowledge links but should not assume field-specific training.

If the author performs the pass in the same conversation, label it `same_context_report_only`. This can find unsupported steps by checking the written evidence; it cannot establish that a new reader would understand. Never report it as a blind test. Record `fresh_context_reader` only if that isolation actually occurred.

## First pass: read forward, including the purpose of each block

As you reach a new block, first record what the preceding text actually establishes and what remains unresolved. Then ask whether the new material has a justified role in that inquiry and whether its prerequisites are available. Use earlier passage locators; later explanations cannot retroactively supply earlier understanding. The reader need not predict the exact next topic, but should be able to understand why it is introduced here. In same-context review this is an explicit evidence restriction, not a claim to have forgotten later content.

At each break in understanding, record:

- section and a short exact quotation;
- the reader's concrete question, including an unresolved “why,” unnamed comparator or missing operation;
- what the report has already established and what it has not;
- whether a reachable knowledge section resolves it, and why the remaining issue belongs in the report or knowledge page;
- severity: blocks the main mechanism/conclusion, blocks a local detail, or only affects phrasing.

Include structural findings even when every sentence is intelligible: an unmotivated route choice, detail before the whole, a comparison without a decision to inform, an experiment without an established hypothesis, or a branch whose result does not update the central answer. Quoting the last sentence of one section and the heading of the next is not evidence of a connection. Do not fix the paper from memory or invent its missing premise. “Needs more detail” is not actionable: specify what the reader cannot connect and why the existing text is insufficient.

## Second pass: reconstruct one explanation, then inspect its parts

Put the headings aside and explain the paper as a connected account, using only the reading package: what difficulty matters, why the investigated approach could change it, what the complete solution does, and how evidence supports or limits the resulting answer. Cite passages for the substantive connections, not just for the individual facts. A list of accurate section summaries fails this test. Do not supply the author's private argument map or planned reading path to the reviewer.

Check the role of the main sections in that account. Where an order appears arbitrary, ask whether the blocks are legitimate parallel evidence under a common question or a collection of unrelated topics. Note where a detail can move later without harming understanding, or must move earlier because another block already relies on it. There is no uniquely correct outline; judge whether the published order supports understanding, not whether it matches the reviewer's preferred order.

For each interaction, first compare it with a direct table, diagram or explanation: does operating it clarify a relationship, or merely reveal text and require remembering hidden values? Recommend removal when the static alternative is clearer. Do not mark a report deficient because it has no interactions. For those retained, inspect the visible states and text fallback. Ask whether the reader knows what changes, what remains fixed, and whether numbers are measured or constructed. A working control does not establish an explanation. Record any conclusion that appears only after guessing how to operate a widget. The source-comparison audit runs separately with the original paper available; never mix that evidence into this pass.

Using only the reading package, reconstruct the ordinary task, the specific research gap (separately from its setting's name), a fair representative alternative, the full method on an example, reasons and tradeoffs for central choices, and the experiment that tests each main claim. Explain what a simpler or removed component would change when the report relies on that distinction. Point to report or knowledge sections supporting every nontrivial step. A reconstruction that requires unstated domain knowledge is a review finding. This is an internal check; do not publish a question-and-answer report merely because review used questions. Inspect the entire argument and its transitions, not just the paragraph cited in user feedback.

## Repair and recheck

Before repairs, test whether the reader can calculate the central example from its stated inputs, explain the direction of the update, and connect its result to the next use. Can they distinguish the authors' documented observations from the report's constructed example, inference or suggested experiment? Can they name a diagnostic outcome that would weaken the proposed explanation? Record unsupported steps, conflicting numbers/roles and a provenance label that could be mistaken for a correctness verdict. Do not require a speculation section or a widget to pass.

Classify the finding before choosing the repair. Missing prerequisites or unmotivated topic choices are organizational failures even when local prose is correct. Reopen the continuous explanation and outline; move, merge, split or defer material as needed, then write the affected prose. Adding “to address this,” a rhetorical question or another introduction does not repair a missing explanation of how the approach works on the problem. Return to primary sources when the missing rationale is factual, and do not manufacture necessity or efficacy to make a story smoother. Missing background, source ambiguity, factual errors and phrasing defects require their corresponding repairs.

Repair at the first dependency rather than in an appended FAQ. For structural changes, reread the entire mainline and check moved material's prerequisites, not just neighboring paragraphs. Repeat the connected reconstruction and local checks for affected reasoning.

Keep a compact record under `data/reviews/` with the report revision, actual review mode, issue → repair/source → supporting section, and unresolved questions. Reviews should refer to the version actually checked. Do not silently inherit a pass after rewriting that version.

Publish when both the whole explanation and its necessary local steps can be reconstructed from the report and linked knowledge, material facts match sources, and unresolved source gaps are explicitly scoped. Mark global organization separately from local comprehension; neither coverage nor a collection of passing section checks establishes the former. No fixed number of iterations proves quality. If further independent review is unavailable, deliver with that limitation rather than asserting an independent pass.
