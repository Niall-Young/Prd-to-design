---
name: extract-prd-design-brief
description: "Use when the user provides a Markdown PRD, pasted PRD text, or a PRD file path. Codex must read the PRD, stop, ask whether it is 0-to-1 or an iteration, collect a Figma URL for iterations, then wait for the user's answer before extracting design-impacting work."
---

# Extract PRD Design Brief

## Hard Stop

When a user provides a PRD, the first run of this skill must only read the PRD and ask the project-type question. The response must not include conclusions, design analysis, design tasks, UI generation, file edits, JSON, Markdown reports, or HTML. The only valid first response after reading the PRD is:

> 我已读完 PRD。这个项目是 0-1 新项目/新功能，还是在现有项目上的迭代？如果是迭代，请同时提供可访问的 Figma 链接。

## Overview

Turn a Markdown PRD into a structured design brief that the report skill can consume. Focus on design work only: pages, flows, UI states, content, data needs, current-design dependencies, and evidence from the PRD.

This skill has a mandatory confirmation gate: read the PRD first, then stop and ask the user whether the work is `zero_to_one` or `iteration`. Do not silently infer the project type from the PRD alone. Do not output a conclusion like "this is an existing-page optimization" before the user confirms. Do not continue to asset extraction, brief extraction, Figma inspection, report generation, or UI image generation until the user answers. If the user confirms `iteration`, require a Figma URL before producing the final brief.

After the confirmation gate is complete, this plugin's default deliverable is the HTML design change report, not a chat-only design analysis. Unless the user explicitly asks for "only the brief", write the brief as `outputs/<project-slug>/design-brief.json` and continue to `$produce-design-change-report`.

## Workflow

1. Get and read the PRD source.
   - If the user gives a file path, read it directly.
   - If the user pastes Markdown, analyze the pasted text and note that local image copying is unavailable unless image files are also provided.
   - v1 supports Markdown only. For PDF, DOCX, or screenshots-only PRDs, ask the user for a Markdown export.

2. Stop and ask for project type.
   - The next assistant response after reading the PRD must be only the confirmation question. Do not add a summary, conclusion, numbered analysis, file output, design brief, UI concepts, HTML, or report skill call in the same response.
   - Ask this exact question in Chinese: "我已读完 PRD。这个项目是 0-1 新项目/新功能，还是在现有项目上的迭代？如果是迭代，请同时提供可访问的 Figma 链接。"
   - Accepted project types are:
     - `zero_to_one`: a new product, new module, or new feature that does not depend on existing design context. Figma is not required.
     - `iteration`: a redesign, optimization, extension, or change to an existing product or existing screen. A Figma URL is required.
   - If the user answers `iteration` without a Figma URL, ask only for the Figma URL and stop again.
   - Even if the PRD strongly implies the type, ask the user. The final `projectType` must come from the user's reply after the PRD was read.

3. Extract PRD image assets when a local Markdown file is available and the confirmation gate is complete.
   - Run from the workspace or plugin root:
     ```bash
     python3 plugins/prd-to-design/scripts/extract_prd_assets.py \
       --prd <prd.md> \
       --output-dir outputs/<project-slug>/assets/prd \
       --json outputs/<project-slug>/prd-assets.json
     ```
   - Bind each Markdown image to the nearest relevant flow node, screen, or requirement by surrounding headings and paragraphs.
   - Preserve remote image URLs as references; copy only existing local files.

4. Record the confirmed project type.
   - Record the confirmation in `projectTypeConfirmation`.
   - The final `projectType` must come from the user's answer, not from model inference.
   - If the answer is `iteration`, set `source.figmaUrl` from the user-provided URL.

5. Extract design-impacting content.
   - Capture target users, business goals, affected scenarios, screens, components, states, content, data fields, permissions, empty/error/loading states, and success metrics.
   - Split requirements into `add`, `change`, `remove`, and `unknown`.
   - Assign priority only when the PRD states or strongly implies it. Otherwise use `unspecified`.
   - Cite source headings or short evidence snippets for each major item.

6. Model flows as multimodal cards.
   - Create `flows[]` whenever the PRD describes a user journey, approval sequence, onboarding, checkout, creation flow, dashboard workflow, or state transition.
   - Each flow node must support text plus optional images. If a PRD image is relevant, set `image.path`, `image.alt`, and `image.source`.
   - Do not flatten flows into a paragraph; the report renderer expects nodes.

7. Write the brief.
   - Use the schema in `references/design-brief-schema.md`.
   - Default language for human-facing values is Chinese unless the PRD is clearly in another language.
   - Include open questions for missing design-critical information.
   - Set `projectType` to `zero_to_one` or `iteration`.
   - For `iteration`, set `source.figmaUrl` to the user-provided Figma URL.
   - Write the brief to `outputs/<project-slug>/design-brief.json`.
   - Do not paste the full design analysis into chat. If the user asked for a PRD design report or general design analysis, continue to `$produce-design-change-report` so the final deliverable is HTML.

## Quality Bar

- Keep design facts traceable to PRD evidence.
- Do not invent UI requirements, pages, or priorities.
- Do not invent, infer, or auto-fill project type. The user must confirm `zero_to_one` or `iteration`.
- Do not state a project-type conclusion before asking. The first response after reading a PRD is only the confirmation question.
- Do not continue past the confirmation question in the same response. Wait for the user's reply.
- Do not proceed with an iteration brief until a Figma URL is provided.
- Do not generate UI concepts before project type confirmation and required Figma collection are complete.
- Do not make a chat-only answer the final deliverable after confirmation. The normal final deliverable is `design-change-report.html`.
- Prefer concise structured output over long prose.
- When a requirement affects multiple screens, list every affected screen.
- When PRD images are ambiguous, attach them to the nearest source section and note uncertainty.

## References

- `references/design-brief-schema.md` defines the expected brief shape.
