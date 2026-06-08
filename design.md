# design.md

## Product Intent

`prd-to-design` is a local Codex plugin that translates Markdown PRDs into
design-ready artifacts. It should help a product or design team move from
requirements to concrete UI work without losing the original PRD intent.

## Target Users

- Product managers who need to turn PRDs into design tasks.
- Product designers who need a concise brief before creating or updating screens.
- Engineers who need a design change report that is specific enough to implement
  or review.

## Core Workflow

1. A user provides a Markdown PRD.
2. `extract-prd-design-brief` reads the PRD only to confirm it is accessible.
3. Codex stops and asks the user to confirm whether the work is 0-1 or an iteration.
   Iterations require a Figma URL before Codex proceeds.
4. After confirmation, `extract-prd-design-brief` produces a structured design
   brief.
5. `produce-design-change-report` writes `outputs/<project-slug>/report.json`
   and renders `outputs/<project-slug>/design-change-report.html`.
6. For iterations, Codex reads the provided Figma file read-only when tools are
   available, or asks for exported frames/screenshots before making current-state
   claims.
7. Codex generates one UI concept image per key page by default.
8. The report is used to review affected screens, interaction changes,
   component needs, risks, and open questions.

## Skill 1: Extract PRD Design Brief

The brief should capture only design-relevant information from the PRD:

- Product context and user goals.
- Affected surfaces, screens, pages, or flows.
- New or changed user journeys.
- UI states, empty states, loading states, error states, and edge cases.
- Data, content, and permission requirements visible in the UI.
- Component, layout, navigation, or interaction implications.
- Constraints from brand, platform, accessibility, or existing design systems.
- Open questions where the PRD is ambiguous.

The extraction should preserve PRD intent and avoid adding unrequested features.
It must not infer project type silently: after reading the PRD, Codex asks the
user to choose 0-1 or iteration. If the user chooses iteration, Codex must
collect a Figma URL before finalizing the brief. Codex must not generate UI,
reports, assets, or design briefs in the same response as the confirmation
question. Codex must not include PRD conclusions or design task lists before the
user answers the project-type question.

## Skill 2: Produce Design Change Report

The final report should be a single `.html` artifact with a Material Design 3
inspired structure. It should prioritize scanability and implementation clarity.
Markdown checklists or alignment notes are not valid final outputs for this
skill unless the user separately asks for them. Chat-only design analysis is
also not a valid final output; the design analysis belongs in the HTML report.

Expected sections:

- Executive summary.
- PRD source assumptions.
- Affected screens and flows.
- Design changes by surface.
- Component and state requirements.
- Content and data requirements.
- Accessibility considerations.
- Risks, dependencies, and open questions.
- Suggested next design actions.
- Generated UI concepts for key pages.
- Connected flowchart diagrams when the PRD describes a process.

## Visual Direction

- Use a calm, professional product design report style.
- Use MD3-style seed color tonal roles exposed as CSS variables.
- Use large rounded "memory card" surfaces for report sections.
- Use connected flowchart diagrams with arrows for process and state flows.
- Prioritize readable hierarchy, spacing, and clear information grouping.
- Keep the layout responsive for desktop and tablet review.
- Use restrained color, accessible contrast, and consistent section structure.
- Avoid decorative visuals that do not explain product behavior.

## Output Principles

- Be faithful to the PRD.
- Make ambiguity visible instead of guessing.
- Convert requirements into actionable design work.
- Separate confirmed requirements from recommendations.
- Keep reports useful for both design review and engineering implementation.

## Non-Goals

- This plugin does not generate final Figma files by default.
- This plugin does not replace product strategy or UX research.
- This plugin does not infer backend architecture unless the PRD explicitly ties
  it to visible UI behavior.
- This plugin does not add unrequested pages, roles, metrics, or workflows.
