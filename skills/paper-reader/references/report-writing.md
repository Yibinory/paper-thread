# Writing an explanation the reader can reconstruct

## Organize by dependencies

Use the whole explanation and reading path from [argument analysis](argument-analysis.md) to choose the order. The source inventory determines what needs coverage; it is not a table of contents. Establish how the chosen approach addresses the concrete difficulty, then let each section develop that account. Do not force every paper through the same task taxonomy or a fixed background/motivation/related-work/method sequence.

Introduce the minimum complete method before its sampling rules, equation variants or implementation details. Use a continuing example where it makes the intervention and its consequences visible. Place comparative and experimental material where it answers a live question in that account. Develop central algebra in the mainline when necessary; secondary detail can form a clearly motivated branch. Keep material adverse evidence visible in the conclusion it qualifies.

Choose headings after deciding those roles. They should name the work the section does; making every heading a question does not create an argument. A roadmap can orient the reader, but cannot substitute for explaining why the proposed route makes sense. Do not impose a fixed template or length.

## Complete comparisons and reasons

“Unlike other methods,” “injects prior knowledge,” “captures structure,” and “improves diversity” are unfinished explanations until the reader can identify the objects and operations involved.

For a comparison important to the contribution, explain a representative prior method by name, its input, its adjustable quantity and its procedure. Then explain the obstacle under this paper's setting, what the new method changes, and why that change may address the obstacle. Do not turn all baselines into weak strawmen or infer their mechanisms from their names. An experimental table may contain peripheral methods without full tutorials, but its decisive comparisons need this context first.

For a design choice, reconstruct the missing intermediate reasoning. For example, predefined color operations can be applied even when those colors are absent from the training images; learning an augmenter from the source gives a different source of variation. This alone does not prove which is better. Explain the mechanism first, then use the paper's actual comparisons to assess the claim. This example is a reasoning pattern, not text to paste into unrelated reports.

## Trace objects, not just stages

A usable algorithm explanation identifies what is stored, computed once, sampled, optimized or updated, and what each stage passes to the next. For alternating optimization, name the frozen and updated parameters. For retrieval, distinguish candidate selection, scoring and final output. For generative editing, identify what stays fixed and what changes.

Follow a concrete example through these objects. A loss table with invented numbers can illustrate a tradeoff, but cannot substitute for explaining how the algorithm obtains a transformed input or updates a parameter. Mark constructed examples once; use them to answer an actual gap. Remove decorative widgets that repeat a simpler claim while leaving the hard step unexplained.

## Explain equations as operations

For the central mechanism, follow the worked-example contract in [research reconstruction](research-reconstruction.md). Calculate an actual intermediate state and its update from explicit inputs, then relate it to the full method. Define shape and fixed/updated status at first use; keep a compact local symbol table when several objects interact. Keep toy inputs, paper measurements and exact derivations visibly distinct. A parameter slider must use the same calculation as the printed example.

Before an equation, state the question it answers. Define symbols, dimensions when relevant, and which quantities are known at that stage. After it, show the non-obvious intermediate step and the resulting decision. Merely defining every letter is insufficient.

Keep the derivation central to a contribution in the report. Put reusable mathematics behind a knowledge link at the moment it is used, with enough local explanation to follow the application. Readers should not have to infer why a theorem applies or why an unavailable quantity can be computed from the stored representation. Distinguish an author theorem, a direct algebraic derivation, and an explanatory reconstruction.

Explain both why a step is valid and why it is useful. A safe filtering bound can still be too loose to save work; a valid optimization objective can still have competing terms. Follow the paper's design that makes the step effective, instead of stopping at the formula's direction or name.

## Connect evidence to a question

Describe what changes between compared runs, what is held constant, what the metric counts, and which claim the result bears on. Then give representative numbers and explain the pattern. Do not bury the reason for the experiment under a list of scores. Explain unfamiliar baseline names before their numbers carry an argument.

A useful limitation follows from a concrete dependency: an unseen cluster cannot be recovered by reranking; a missing operation cannot generate that style. Place these conditions where needed. Consolidate repeated general cautions into one discussion. Repeating “does not guarantee” after each paragraph adds neither explanation nor rigor.

## Prose that performs work

Use evidence labels for substantive reconstructions and proposed diagnoses as specified in the research guide. Put a practical diagnostic beside the mechanism whose premise it tests, with an observable symptom and the cost of the proposed repair. Do not add a stock “first version fails” paragraph to every subsection, or infer a private author history from rhetorical wording. Semantic colors distinguish roles and provenance; they do not replace explanation or certify a claim.

Prefer specific subjects and verbs: the classifier supplies a gradient; the table stores a segment minimum; the queue chooses an unexplored hypothesis. Replace abstract praise and verdicts with the intermediate facts that justify them. Do not mechanically rewrite every sentence into “not X but Y.” Read neighboring paragraphs in context: each should develop the current question, establish a necessary premise or contribute a clearly related branch. “Therefore,” “next,” and a repeated keyword do not supply that relation.

Knowledge pages should be independently useful, but the report owns the mappings and reasoning specific to this paper. Report completeness is judged by a reader's supported reconstruction, not by whether all conventional headings appear.
