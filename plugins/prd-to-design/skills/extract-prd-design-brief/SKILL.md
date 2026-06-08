---
name: extract-prd-design-brief
description: "Use when the user provides a Markdown PRD, pasted PRD text, or a PRD file path and wants Codex to extract design-impacting work: project type, users, goals, screens, flows, multimodal PRD assets, design requirements, priorities, and open questions."
---

# Extract PRD Design Brief

## Overview

Turn a Markdown PRD into a structured design brief that the report skill can consume. Focus on design work only: pages, flows, UI states, content, data needs, current-design dependencies, and evidence from the PRD.

## Workflow

1. Get the PRD source.
   - If the user gives a file path, read it directly.
   - If the user pastes Markdown, analyze the pasted text and note that local image copying is unavailable unless image files are also provided.
   - v1 supports Markdown only. For PDF, DOCX, or screenshots-only PRDs, ask the user for a Markdown export.

2. Extract PRD image assets when a local Markdown file is available.
   - Run from the workspace or plugin root:
     ```bash
     python3 plugins/prd-to-design/scripts/extract_prd_assets.py \
       --prd <prd.md> \
       --output-dir outputs/<project-slug>/assets/prd \
       --json outputs/<project-slug>/prd-assets.json
     ```
   - Bind each Markdown image to the nearest relevant flow node, screen, or requirement by surrounding headings and paragraphs.
   - Preserve remote image URLs as references; copy only existing local files.

3. Classify project type.
   - `greenfield`: PRD describes a new 0-to-1 product or feature with no existing design dependency.
   - `iteration_with_design`: PRD describes a redesign, optimization, or iteration and includes or asks for an existing Figma/design file.
   - `iteration_no_design`: PRD describes an iteration but no design file is available; the next skill should ask for screenshots.
   - `unknown`: PRD does not provide enough evidence. Add a specific open question instead of guessing.

4. Extract design-impacting content.
   - Capture target users, business goals, affected scenarios, screens, components, states, content, data fields, permissions, empty/error/loading states, and success metrics.
   - Split requirements into `add`, `change`, `remove`, and `unknown`.
   - Assign priority only when the PRD states or strongly implies it. Otherwise use `unspecified`.
   - Cite source headings or short evidence snippets for each major item.

5. Model flows as multimodal cards.
   - Create `flows[]` whenever the PRD describes a user journey, approval sequence, onboarding, checkout, creation flow, dashboard workflow, or state transition.
   - Each flow node must support text plus optional images. If a PRD image is relevant, set `image.path`, `image.alt`, and `image.source`.
   - Do not flatten flows into a paragraph; the report renderer expects nodes.

6. Output the brief.
   - Use the schema in `references/design-brief-schema.md`.
   - Default language for human-facing values is Chinese unless the PRD is clearly in another language.
   - Include open questions for missing design-critical information.

## Quality Bar

- Keep design facts traceable to PRD evidence.
- Do not invent UI requirements, pages, or priorities.
- Prefer concise structured output over long prose.
- When a requirement affects multiple screens, list every affected screen.
- When PRD images are ambiguous, attach them to the nearest source section and note uncertainty.

## References

- `references/design-brief-schema.md` defines the expected brief shape.
