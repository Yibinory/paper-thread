# Content authoring contract

The app is a local Chinese paper reader. Author JSON files in `data/reports` and `data/concepts`. IDs are permanent. No scripts, event handlers, external CSS, iframes or page scaffolds in HTML. Use semantic HTML: p, ul/ol/li, strong, em, blockquote, table/thead/tbody/tr/th/td, figure/img/figcaption, details/summary, code/pre, div/span, h3, a. LaTeX uses `\\(...\\)` or `\\[...\\]` inside HTML strings; renderer uses bundled KaTeX. Escape JSON properly with Python json.dump.

## Document JSON

Required keys: `id`, `kind` (`report` or `concept`), `title`, `subtitle`, `summary`, `domain`, `tags` (array), `status` (`ready`), `sections` (array of `{id,title,html}`), `sources` (array of `{id,title,url}`; locator can be additional text). Concepts also require `aliases` (array), `scope` (string), `not_this` (array of distinctions), `semantic_terms` (array of short Chinese AND English search phrases), `prerequisites` (array of concept IDs).

Reports additionally require `paper`: `{title,authors,year,venue,pdf,pages,coverage}`. `pdf` is the repository-relative managed path returned by `paper.py import-paper`, normally `data/papers/SHA256.pdf`; legacy `test_paper/` paths remain supported. Users provide links or accessible local files; the agent locates the full-text PDF and imports it, creating directories automatically. Do not require users to prearrange files. Record `paper.sha256` and the original public `paper.source_url` when available; the importer also keeps provenance under `.local/imports/`. A paper page is resolved by the agent, not parsed by the importer. `pages` comes from reading the actual PDF, not the download response. `coverage` honestly states what was read and unavailable supplements/code. `reading_minutes` approximate reading time; `contributions` 2–3 short strings. Report sections should be connected technical explanation, not a Q&A or a list of abstract claims. Length follows the reasoning needed for independent understanding; no character-count target. Explain representative alternatives and the missing steps behind central design choices. No prerequisite list in the opening. Do not claim executing code/reproducing experiments unless actually performed. Annotate teaching examples as constructed; do not invent empirical measurements. All key experimental numbers/claims have adjacent source links. Look for publicly available supplements and pertinent author code when they resolve a mainline gap; record what was actually read. Mark genuinely unavailable material and its consequence without fabricating an answer. Use specific section titles.

## Links

Knowledge: `<a data-concept="k-pq">乘积量化</a>`; optionally `data-section="mechanism"` if that exact section exists. Only link on first substantive use within a section; no forced prerequisites panel. Explanation of paper-specific use stays in report. For new-paper-specific mechanisms explain in report instead of extracting entire contribution out.

Paper evidence: `<a data-source="paper" data-page="6">原文 §4，PDF p.6</a>`. `data-source="paper"` resolves to the report PDF. Other sources: `<a data-source="SOURCE_ID">来源</a>` using sources list. On concept pages use explicit source URLs and page fragments in sources. Every external link should be an authoritative source supporting that paragraph. Do not browse review-version private uploaded paper content online. Do not upload PDFs anywhere.

Figure: `<figure><img src="/data/figures/NAME.png" alt="Meaningful description"><figcaption>Explain what to see, paper provenance and page.</figcaption></figure>`. Use pdfplumber rendering and crops; no fabricated diagrams labelled as original. Self-drawn diagrams can use simple ordered HTML steps. For interactive explanations use the structured contracts below, with surrounding explanation and a static fallback.

## Knowledge and review

No fixed concept catalog: inspect `paper.py inventory` before choosing an existing ID or creating one. `semantic_terms` are human/agent-readable functional search phrases, not embedding vectors. The calling agent resolves semantic identity from definitions and use; `search` supplies lexical candidates only.

Knowledge pages are detailed tutorials for first-time learners, independently sourced from the concept's original/foundational works, authoritative expositions and relevant variant/application papers. Actively research those sources for new or substantive rewrites; the triggering paper is not the default conceptual authority. Explain the problem, theory and central derivations, complete worked calculations, practical application, assumptions, failure cases and meaningful variants. Do not cap depth at the triggering report's needs or use a word quota. Preserve meaningful section IDs and place sources next to supported claims. State uncertain historical attribution or unavailable originals honestly.

Knowledge pages teach corrected, justified content directly. Keep source mistakes, original erroneous expressions and correction provenance in audit records; do not include source-error panels or errata citation titles in tutorials. Recheck dependent derivations/examples after correcting them. Valid counterexamples that explain the correct conditions remain appropriate. Paper reports retain visible, evidenced criticism of their specific source paper.

Link unfamiliar reusable foundations where they are used, explaining their immediate role first. Verify the linked explanation can support the next step. Distinguish required prerequisites from optional related applications: required foundations must not form cycles; optional related links must not create circular explanations. Do not add an introductory prerequisite list.

Follow `skills/knowledge-curator/references/knowledge-review.md` before publishing new or substantively rewritten concepts. Keep source/teaching coverage, item-level correctness, reader reconstruction and transfer, link journeys and rendering checks separate, tied to the final digest and linked revisions. `review-pack k-ID --draft FILE --to DIR` produces `concept.json`, reachable `knowledge.json` and neutral instructions. Label same-context review `same_context_knowledge_only`; parser success is not a comprehension pass. Resolve core teaching failures before setting the page ready.

Each paper has one current report with a stable ID. Check the report inventory before creating an ID. For regeneration, draft from sources in `.local/drafts/`, record reading questions and their resolution under `data/reviews/`, then update the existing report after review. Do not publish draft iterations, version-suffixed IDs or comparison pages. Internal snapshots support storage safety and audit records; the reader and reading bundle expose only the current report. Use `review-pack` to isolate report, reachable knowledge and figures. Record `same_context_report_only` or `fresh_context_reader` truthfully. Content review, source validation and rendering checks are separate evidence. Passing the schema is not proof of comprehension.

## Correctness findings and reading hierarchy

Coverage and correctness are separate. Follow `skills/paper-reader/references/correctness-audit.md` to inventory and analyze every scientific claim, formula, inference and conclusion. Keep item-level evidence, calculations, statuses and dependencies in `data/reviews/`, tied to source versions and the final draft. Explicitly name unchecked scope; no full-verification badge or automatic pass from formatting checks.

Use headings, `strong` for important statements, `em` for explanatory emphasis, and ordinary math delimiters; the shared `web/reading.css` supplies consistent colors in reports, knowledge pages and drawers. Do not embed color styles or sprinkle emphasis over whole sections. Color does not certify correctness.

For a paper-report finding that needs to stand out, use `<div class="reading-note" data-note="error"><h3>已核实的错误：具体问题</h3><p>原文定位、断言、核查依据及影响。</p></div>`. Other roles: `uncertain` (unresolved ambiguity/inconsistency), `scope` (unsupported extension or evidence limit), `definition` (a useful definition), `conclusion` (a supported takeaway). Choose by meaning, not decoration; these are optional. Every note needs a visible descriptive heading. Red error styling requires decisive evidence; an unverified statement uses `uncertain`, not `error`. Keep important findings visible; optional details can hold lengthy supporting calculations. Print retains headings and borders so interpretation never depends on color alone.

## Structured interactions

`interactives` is optional and may be omitted or empty. Use controls only when they explain a relationship better than a direct static presentation. A short sequence or small comparison table does not need an interactive wrapper. Do not impose a widget quota on reports.

Use `interactives` as an object keyed by a stable ID. Put `<div data-interactive="ID"><p>Complete default example and conclusion as static text.</p></div>` at the application point. Every configuration has `type`, `title`, `question` (the action/observation), `provenance` (measured data or constructed calculation, with locator). Add an adjacent normal source link. All configuration strings are plain text and escaped by the shared renderer. No code in configuration. The fallback remains if rendering is unavailable and is printed instead of controls.

Supported contracts in `web/interactions.js` / `interactions.py`:

- `trace`: `steps` (at least two), each `{label,caption,changes,holds,reason,states:[{label,value,state}]}`. `state` is `active`, `fixed`, or `read`. Use the states to expose objects and current values, not duplicate generic prose. Steps can represent an algorithm or explicitly named alternative variants.
- `evidence`: `measure`, `columns` (nonempty list of header strings including units/directions), `cases:[{label,condition,rows:[{label,values}],takeaway}]`. Values correspond exactly to columns. Conditions and takeaways are visible when selected; do not hide contrary cases from the static text.
- `pq-bound`: fixed worked example with `minimum:0.1`, `values` (eight finite values ≥ 0.1). Controls expose distance threshold and quantization step; renderer labels the eight-subspace arithmetic, not machine performance. Change the renderer and validator together for different assumptions.
- `rabitq-bound`: fixed worked-example `parameters:{dimension:256,a:0.8,ro:2,rq:3,numerator:0.4}`. Controls expose epsilon, threshold and an illustrative extra inner-product error budget. Not an empirical confidence calculator. Changing the example requires updating both renderer labels and validator.

Older `data-demo` content remains readable for historical revisions. New authoring uses the contracts above; it does not insert unrelated legacy demos. New types must be shared, reviewed renderers with arithmetic/state tests and a usable fallback.

Do not author `previous_revision`; report comparison is not supported. `build` includes current reports and the knowledge revisions they cite. Legacy comparison URLs open the current report.

Before publication keep a source-unit coverage matrix and a correctness ledger for every scientific claim, formula, inference and conclusion under `data/reviews/`, separately from the report-only reader review. All refer to the final draft digest, which includes interaction configurations. Coverage decisions distinguish explained, brief, linked, deliberately omitted and unverified material; do not claim completeness from automated field checks.
