# Interactions that explain a paper

Start with the clearest static presentation. Before adding an interaction, name the reader's specific difficulty and explain what operating the control makes easier to understand than a paragraph, table or diagram. If that benefit is unclear, use the static presentation. Zero interactions is a valid outcome; reducing paragraph density is not itself a reason to add controls.

For a retained interaction, record its question, inputs, visible intermediate state, expected observation, source or derivation, and limits. Do not add a generic slider merely because the paper mentions an optimization, graph or probability. These notes belong in the authoring/review record, not as interface-design commentary in the report.

Useful patterns:

- Trace: useful when a changing diagram or state makes a transition difficult to see all at once. A few buttons that merely replace explanatory paragraphs are usually worse than a visible sequence. Keep hypotheses and observed evidence distinguishable.
- Calculation: change a parameter that changes a decision; show intermediate arithmetic and both sides of the decision threshold. Cover a boundary or counterexample, not just a favorable default.
- Evidence comparison: use controls only when the data volume or linked views justify them. A small table should expose conditions together so readers can compare without remembering hidden values. Preserve units, metric direction, baseline and source. Never fabricate a curve by interpolating a few table cells.

Put the component immediately after the explanation it makes inspectable. State the useful action, such as changing a threshold from 3.0 to 3.5 to see why refinement becomes necessary. Explain what to notice. Limit each component to a clear question; there is no quota of widgets per section or paper.

Prefer a complete, informative figure as the default state, with a small control below it. Change a quantity, highlight a dependency or advance a computed state; do not merely swap paragraphs. A parameter control should visibly change a curve, geometry, distribution or decision region as well as its numerical readout. Keep comparison objects in stable positions and on common scales. Expose a meaningful boundary, competing effect or failure case. Do not interpolate measured cells into an invented experimental curve; derive teaching curves from a stated model.

Color is a second notation: use a few consistent roles (input, transformation, prediction, objective) across the worked example and its figure, with written names/line styles as well. Use the shared theme variables, not a new color for each box. Provenance labels and correctness findings are a different semantic dimension. Check light/dark themes and print; never rely on red versus green alone. Large labels and uncluttered lines matter more than animation. No automatic animation or decorative dashboard. Keep input focus stable while redrawing, support native keyboard controls and reset, and respect reduced-motion preferences.

Every widget has a text fallback in the report, sufficient to understand its default example and key conclusion. Printing must expose that fallback. Label constructed examples as teaching calculations; do not imply a model ran, a graph was inferred, an image was medically edited, or an experiment was reproduced. Mathematical quantities use the same units and assumptions as the surrounding explanation. Separate paper measurements, algebraic consequences and illustrative inputs.

Use trusted shared renderers through the `interactives` schema in `CONTENT_SCHEMA.md`. Content contains no executable code. Prefer extending a reusable renderer for a real explanatory need to hardcoding a paper's identity in the application. Unknown or failed components retain the fallback. Include configurations in reader review packs, so the review sees what the reader can operate.

Before publication, reconsider each interaction against its static alternative. Remove controls that add clicks, hide comparisons, or repeat the explanation without a concrete comprehension benefit; retain their useful content in the direct explanation. For those retained, verify reset, applicable endpoints, a meaningful change, keyboard controls, responsive layout, and the static explanation. For calculations, test invariants (for example a conservative distance bound cannot exceed the example's exact distance), not the presence of particular sentences. Report actual checks, not an assumed pass.
