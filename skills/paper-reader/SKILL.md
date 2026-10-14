---
name: paper-reader
description: 接收论文链接、附件或本地 PDF，获取原文并生成可独立理解的中文 HTML 报告，复用知识库，逐项核查主张、公式、推理与结论，指出错误和证据边界，并检查覆盖与读者理解。适用于论文讲解、整篇重新生成及阅读反馈后的再生成。
---

# Paper Reader

Locate the PaperThread project root containing both `paper.py` and `CONTENT_SCHEMA.md`: first inspect the current workspace and its ancestors, then the resolved skill path and its ancestors. Do not assume this skill is a symlink or that a user-level installation contains the application. If no project is available, ask for its location. Run commands from that root with Python 3.10+: `python3` on macOS/Linux, `py -3` or `python` on Windows, or the project virtual environment (`.venv/bin/python` / `.venv/Scripts/python.exe`). The examples below use `python3`; substitute the available interpreter. Read and write content files as UTF-8. Read the schema and [writing guide](references/report-writing.md). The calling agent reads, reasons, browses and writes; the local tool stores and retrieves documents. There is no local language/embedding model to install or index to build.

## Accept a paper link or file and manage the source

Accept paper landing-page links (including DOI/arXiv/publisher pages), direct PDF URLs, accessible attachments, local PDF paths anywhere the agent can read, and batches of these inputs. Do not require the user to download, rename or move files into the project, or create storage directories.

For a paper page, open it and locate the full-text PDF using the agent's browser/search tools; verify title, authors and the requested version. Resolve redirects and select an accessible primary source rather than guessing a PDF URL. Then import the resolved PDF:

```sh
python3 paper.py import-paper "RESOLVED_PDF_URL" --source-url "ORIGINAL_PAPER_PAGE_URL"
```

For a direct PDF URL or local file, use `import-paper "URL_OR_LOCAL_PATH"`; a local file is copied, not moved. An attachment can first be obtained using the host's normal attachment tools, then imported. If an authenticated browser download is needed, import that downloaded file and pass the public paper page as `--source-url`. Do not ask the user to reorganize their files as a fallback. If full text is genuinely inaccessible after checking available primary sources, explain the access gap; do not substitute an abstract-only account for a full report.

The importer creates `data/papers/` automatically, returns the managed `pdf` path, local source `url` and `sha256`, and records origins under `.local/imports/`. It deduplicates identical bytes; this does not determine whether two versions belong to the same paper. It checks the PDF header, not scientific identity or completeness: open and read the imported file, verify the actual version/page count and inspect formulas and figures before relying on it. Use returned paths instead of inventing filenames. Retain the original public link in the report's sources and `paper.source_url` when available, and record `paper.sha256`. Put extraction and drafts under `.local/`; create needed directories yourself. Existing reports using `test_paper/` remain valid and need no migration.

## What the reader must be able to do

Explain how the paper's question leads to its chosen approach, how that approach works as a whole, and how the evidence changes what the reader can conclude. The reader should be able to reconstruct this connected explanation, not just summarize each section separately. They have not read the paper and may be new to its field.

Maintain one current report per paper. Before creating an ID, inspect `inventory --kind report` and match the paper by title, authors and source. Reuse the existing ID when updating or regenerating that paper; do not create version-suffixed IDs, parallel published reports or comparison pages.

When asked to regenerate after feedback, treat the current report as a diagnostic sample. Record its failures, improve this workflow, and write a new draft from source evidence and a new explanation outline. Do not use paragraph substitutions on the old report as a substitute for testing the revised skill. Keep draft iterations outside the published collection and publish only the reviewed final draft to the same ID. Internal storage snapshots and review records are not additional report deliverables.

## Read to answer the missing reasoning

Verify the supplied version and read the introduction, method, relevant figures, results, discussion and available supplements. Apply [argument reconstruction and report architecture](references/argument-analysis.md) before choosing section headings: distinguish the setting from the specific research gap, establish why the chosen intervention could address it, reconstruct the complete mechanism, and connect it to discriminating evidence. Save both the source-grounded argument and its planned reading path in one review record. A list of contribution cards or individually reasonable sections does not establish that path.

If a central sentence cannot be explained, first locate the missing definition or reasoning. Follow references to public appendices, author code and relevant baseline papers when needed. Search is a normal part of generation; offline completion is not a goal. Do not turn a missing local appendix into a permanent excuse without checking its public availability. Read only the code needed to settle an explanation; state whether it was inspected or actually run. Do not upload private material or externally search distinctive text from an unpublished/private draft.

Treat the paper itself as fallible. Apply the [correctness audit](references/correctness-audit.md): inventory and examine every scientific claim, formula (including inline and appendix equations), inference and conclusion, not only headline contributions. Independently derive/recalculate where possible, inspect source conditions and primary dependencies, and distinguish confirmed errors, unsupported scope, ambiguity/inconsistency and unverified items. Keep source locators and a detailed item-level ledger. Do not hide inconsistent notation or an unsupported proof step, silently repair the original, or claim exhaustive verification from a partial review.

## Resolve reusable knowledge with the agent

Before outlining, inventory substantive source units using [source coverage and claim audit](references/source-audit.md): methods, assumptions, theory, main and secondary experiments, limitations, and available appendices. An outline derived only from the abstract or the previous report cannot establish coverage.

Start with `inventory --kind concept`. It returns compact definitions, aliases, scope, distinctions, section IDs and revisions. Follow `next_offset` for remaining entries; use `--domain` only after considering neighboring domains and overloaded terms. With a small library, read the whole compact inventory, not every article body.

The agent compares meaning, assumptions, granularity and the use in this paper. `search QUERY --context CONTEXT --kind concept` is a lexical convenience, not a semantic verdict. Try alternative names where useful, then `get ID` for candidates. A failed keyword search never establishes absence. Before adding a concept, check the relevant inventory and document why the closest candidate does not cover it.

- Same concept and adequate explanation: reuse ID, section and revision.
- Same concept with a missing explanation: improve the knowledge page through [knowledge-curator](../knowledge-curator/SKILL.md). Its tutorial must independently research the concept's original/foundational work and teach a beginner the theory, worked application and pertinent variants; do not size it as a brief appendix to this paper. New or substantively revised knowledge passes its own source, correctness, comprehension and link reviews before this report cites it.
- Verified synonym: add an alias; do not equate a general method with a variant.
- Distinct, reusable background that is needed here: create a knowledge page before linking it.
- A paper's contribution, custom symbol or paper-specific design reason: explain it in this report.

At the point of application, say what a concept does here and then offer its link. A link must not carry the paper's missing causal step or an unnamed baseline comparison. One-sentence context can remain inline; no introductory prerequisite list.

## Draft, read as a reader, then publish

Before drafting sections, use the argument guide to write a short, continuous explanation of the whole paper and check the reader's necessary intermediate steps. Derive the outline from that explanation; do not fill conventional headings independently and join them afterward. Establish a usable whole-method model before detail, and give evidence and technical branches a role in the same inquiry. Then write the draft as JSON outside the published collection, e.g. `.local/drafts/PAPER.json`. Use the writing guide to decide what needs derivation, an example, a figure or a knowledge link.

Default to direct explanation with text, tables or figures. Add an interaction only when it makes a specific relationship easier to understand than the best static presentation; apply the [interaction guide](references/interaction-design.md) to make that choice. A paper may have no interactions. Do not allocate a number per paper or treat the existence of a renderer as a reason to use it. Keep the essential explanation readable without operating a widget.

Before publication, use [reader review](references/reader-review.md). Build a pack with:

```sh
python3 paper.py review-pack r-ID --draft .local/drafts/PAPER.json --to .local/review-packs/r-ID
```

The pack contains only the draft, reachable knowledge and figures. A reader pass must not consult the original paper or fill gaps with the author's memory. If an independent fresh context is available and agent delegation is authorized, give the reviewer only the pack and its neutral instructions. Otherwise do a report-evidence-only self-review and label it accurately; the same conversation is not an independent blind test. Do not pretend to forget the source.

Record concrete blocking questions and unsupported teach-back steps. Apply the whole-report architecture review as well as local comprehension checks: a fluent answer within each section is insufficient when its purpose has not been established. Repair structural failures by revising the explanation and its organization, including moving, merging or deferring material where needed; then reread the complete mainline. Connecting phrases, rhetorical questions and an introductory roadmap cannot substitute for missing reasoning. Keep review notes separate from the report. Resolve problems that block understanding of the contribution, or visibly delimit what the available evidence cannot explain. Reaching a word count, adding caveats or passing formula checks does not satisfy this gate.

Then finish two separate source checks. The [coverage audit](references/source-audit.md) maps every substantive source unit to a report location or an explicit, justified omission. The [correctness audit](references/correctness-audit.md) checks every inventoried claim, formula and conclusion against derivations, assumptions and evidence; being covered is not being correct. Reconcile the abstract and conclusion with the detailed findings. Show confirmed errors and their reasoning visibly at the point of use; state unresolved scope accurately. Fix missed contributions, unsupported strengthening and missing contrary results before publication, then recheck changed explanations with the reader pass. Tie coverage, correctness and reader records to the final draft digest, including interaction configurations. Do not inherit a full-audit pass from older reports or call a parser/numerical smoke test a proof.

After these reviews, save with `save FILE --expected-revision REV` for an existing ID, or `save FILE` for a new paper. This updates the single current report. Preserve section anchors when their meaning remains applicable. Run `check` and `build`; check figures/formulas, interaction calculations and representative browser reading. `build` pins new knowledge references. Existing pins change only after reviewing the changed knowledge; do not refresh the whole library as a routine step. Reader notes remain untouched. Do not add `previous_revision` or version-comparison links.

Deliver the reading entry, what was generated, and the actual review mode and remaining limitations. Optional `export` creates a portable reading copy; offline execution of the authoring skill is not a requirement.
