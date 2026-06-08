---
name: produce-design-change-report
description: Use after a PRD design brief exists, or when the user asks for an HTML design change report from a PRD plus optional Figma link or screenshots. Produces Chinese MD3-style HTML reports, flow card diagrams, and generated UI concept image references.
---

# Produce Design Change Report

## Overview

Create an `HTML + assets/` design change report from a structured PRD design brief. The report must explain what the design needs to add, change, or remove, show multimodal flow cards, and include generated UI concept images for key pages.

## Workflow

1. Confirm inputs.
   - Required: a design brief from `$extract-prd-design-brief`, or enough PRD content to produce one first.
   - Optional: Figma URL for existing design, screenshots, product notes, brand color, or generated UI image paths.
   - If the project type is `greenfield`, do not require Figma.
   - If the project type is `iteration_no_design`, ask for screenshots before making current-state claims.

2. Read current design context.
   - If a Figma URL is provided and Figma tools are available, load the Figma use skill first and inspect the file read-only.
   - Never create, edit, delete, rename, or reorganize Figma nodes for this skill.
   - If Figma tools are unavailable, explain the fallback and use user-provided screenshots.
   - Record whether each observation came from PRD, Figma, screenshot, or assumption.

3. Generate UI concept images.
   - Use the image generation skill/tool for UI mockups.
   - Default: generate one concept image per key page.
   - Save final project-bound images under `outputs/<project-slug>/assets/generated/`.
   - Reference image paths in `generatedConcepts[]`; do not leave report-referenced images only under the default image generation directory.

4. Prepare report JSON.
   - Use `references/report-json-schema.md`.
   - Include a `seedColor` when Figma, screenshot, or brand input provides one.
   - If no seed color is available, omit it; the renderer will use a stable default and mark the source as default.
   - Include all PRD flows as `flows[]`; flow nodes can include `image.path` and `image.alt`.

5. Render HTML.
   - Run:
     ```bash
     python3 plugins/prd-to-design/scripts/render_design_change_report.py \
       --input outputs/<project-slug>/report.json \
       --output outputs/<project-slug>/design-change-report.html
     ```
   - The output must be a static HTML file with relative image paths.

## HTML Requirements

- Use Material Design 3 style tonal roles exposed as CSS variables.
- Use large rounded "memory card" surfaces: 24px-32px default radius.
- Use cards for report sections, flow nodes, generated concepts, risks, and open questions.
- Avoid strong gradients and marketing hero layouts; this is a design work report.
- Ensure responsive desktop/mobile layout and no text overflow.

## Flow Card Rules

- If the PRD has flows, the HTML must include a flow card diagram section.
- Render flows with native HTML/CSS, not as one static image.
- Each node card supports title, description, role/status tags, design action, evidence source, and optional image thumbnail.
- Desktop should show horizontal flow tracks with arrows. Mobile should stack nodes vertically.

## Quality Bar

- Separate confirmed current-state findings from assumptions.
- Do not claim Figma analysis occurred when the Figma tool was unavailable.
- Keep generated image prompts aligned with the PRD and current design context.
- Put unresolved product/design ambiguity into open questions.
- Always report the final HTML path and asset folder.

## References

- `references/report-json-schema.md` defines report JSON consumed by the renderer.
- `references/html-style-spec.md` defines MD3 card visual requirements.
