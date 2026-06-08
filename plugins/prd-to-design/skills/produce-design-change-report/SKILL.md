---
name: produce-design-change-report
description: Use only after a PRD design brief exists with a user-confirmed project type. If the input is a raw PRD or an unconfirmed brief, Codex must read it, stop, ask whether it is 0-to-1 or an iteration, and wait. For iterations, require a Figma URL before reporting. Produces a Chinese MD3-style `.html` report with CSS-rendered flowchart diagrams and generated UI concept image references.
---

# Produce Design Change Report

## Output Contract

After the confirmation gate is complete, the final deliverable must be a file:

- `outputs/<project-slug>/report.json`
- `outputs/<project-slug>/design-change-report.html`

Do not answer with the report content as inline chat prose. Do not stop after listing "设计需要做的事". The design analysis, Figma comparison, flowchart, risks, and next actions must be inside `design-change-report.html`. The final chat response should only give the HTML path, asset folder, and any validation notes.

## Hard Stop

If the user provides a raw PRD, pasted PRD text, or a PRD file path, this skill must not generate a report yet. First read the PRD, then reply only with:

> 我已读完 PRD。这个项目是 0-1 新项目/新功能，还是在现有项目上的迭代？如果是迭代，请同时提供可访问的 Figma 链接。

Do not include conclusions, design analysis, design tasks, UI concepts, report JSON, Markdown, HTML, or file edits in that response.

## Overview

Create an `HTML + assets/` design change report from a structured PRD design brief. The report must explain what the design needs to add, change, or remove, show multimodal flowchart diagrams, and include generated UI concept images for key pages.

The final user-facing artifact must be a static `.html` file. Markdown files can only be scratch notes if the user explicitly asks for them; do not present `.md` checklists, alignment notes, or Markdown reports as this skill's output.

## Workflow

0. Enforce the confirmation gate.
   - If the user provides raw PRD content, a PRD path, or a brief without `projectTypeConfirmation.status: "user_confirmed"`, do not generate UI concepts, report JSON, assets, or HTML yet.
   - First read the PRD enough to know it was accessible, then stop and ask the exact question: "我已读完 PRD。这个项目是 0-1 新项目/新功能，还是在现有项目上的迭代？如果是迭代，请同时提供可访问的 Figma 链接。"
   - After asking, wait for the user's next reply. Do not continue in the same response. Do not include a conclusion, summary, or design task list.
   - If the user replies that it is an iteration but does not provide a Figma URL, ask for the Figma URL and stop again.
   - Only continue when the user has confirmed `zero_to_one`, or confirmed `iteration` and provided a Figma URL.

1. Confirm inputs after the gate is complete.
   - Required: a design brief from `$extract-prd-design-brief`, or enough PRD content to run that skill first.
   - The brief must include a user-confirmed `projectType`: `zero_to_one` or `iteration`.
   - If the project type is missing or only inferred, return to step 0. Do not proceed.
   - If the project type is `zero_to_one`, do not require Figma.
   - If the project type is `iteration`, require `source.figmaUrl`. If it is missing, stop and ask the user for a Figma URL before making the report.
   - Optional after the required inputs: screenshots, product notes, brand color, or generated UI image paths.

2. Read current design context.
   - For `iteration`, inspect the provided Figma file read-only when Figma tools are available.
   - Never create, edit, delete, rename, or reorganize Figma nodes for this skill.
   - If Figma tools are unavailable, explain that the Figma URL was collected but cannot be inspected in the current environment, then ask for screenshots or exported frames before making current-state claims.
   - Record whether each observation came from PRD, Figma, screenshot, or assumption.

3. Generate UI concept images only after confirmation.
   - This step is forbidden until step 0 is complete.
   - Use the image generation skill/tool for UI mockups.
   - Default: generate one concept image per key page.
   - Save final project-bound images under `outputs/<project-slug>/assets/generated/`.
   - Reference image paths in `generatedConcepts[]`; do not leave report-referenced images only under the default image generation directory.

4. Prepare report JSON.
   - Use `references/report-json-schema.md`.
   - Write the report JSON to `outputs/<project-slug>/report.json`; do not keep it only in chat.
   - Include a `seedColor` when Figma, screenshot, or brand input provides one.
   - If no seed color is available, omit it; the renderer will use a stable default and mark the source as default.
   - Include all PRD flows as `flows[]`.
   - Model each flow as a flowchart: every node should have a stable `id`, `type`, `title`, `description`, and `designAction`.
   - Use node `type` values such as `start`, `process`, `decision`, `data`, and `end` when the PRD supports them.
   - Add `edges[]` with `from`, `to`, and optional `label` whenever a flow branches or loops.

5. Render HTML.
   - Run:
     ```bash
     python3 plugins/prd-to-design/scripts/render_design_change_report.py \
       --input outputs/<project-slug>/report.json \
       --output outputs/<project-slug>/design-change-report.html
     ```
   - The output path must end in `.html`.
   - The output must be a static HTML file with relative image paths.
   - After rendering, verify the file starts with `<!doctype html>` and includes a `.flow-diagram` section when the PRD has flows.
   - Report the final `.html` path and asset folder. Do not attach `.md` files or paste report sections as the deliverable for this skill.

## HTML Requirements

- Use Material Design 3 style tonal roles exposed as CSS variables.
- Use large rounded "memory card" surfaces: 24px-32px default radius.
- Use cards for report sections, generated concepts, risks, and open questions.
- Use a real flowchart section for flows: connected nodes, arrow connectors, node types, and optional branch labels.
- Avoid strong gradients and marketing hero layouts; this is a design work report.
- Ensure responsive desktop/mobile layout and no text overflow.

## Flowchart Rules

- If the PRD has flows, the HTML must include a flowchart diagram section.
- Render flows with native HTML/CSS, not as one static image.
- Do not render flows as Markdown bullet lists, plain checklists, or prose-only summaries.
- Each flowchart node supports title, description, node type, role/status tags, design action, evidence source, and optional image thumbnail.
- Desktop should show connected horizontal flowcharts with arrows. Mobile should stack nodes vertically with downward connectors.
- Branching or conditional flows should include labeled edges in `edges[]`; the HTML should display those labels near the diagram.

## Quality Bar

- Separate confirmed current-state findings from assumptions.
- Do not infer project type inside this skill; use the user-confirmed value from the brief.
- Do not state a project-type conclusion before asking the confirmation question.
- Do not generate UI concepts before the confirmation gate is complete.
- Do not produce an iteration report without a Figma URL.
- Do not hand back Markdown as the final report. The final report must be `.html`.
- Do not hand back inline design analysis as the final report. If the answer contains section headings like "设计需要做的事", those sections must be in the generated HTML file, not only in chat.
- Do not claim Figma analysis occurred when the Figma tool was unavailable.
- Keep generated image prompts aligned with the PRD and current design context.
- Put unresolved product/design ambiguity into open questions.
- Always report the final HTML path and asset folder.

## References

- `references/report-json-schema.md` defines report JSON consumed by the renderer.
- `references/html-style-spec.md` defines MD3 card visual requirements.
