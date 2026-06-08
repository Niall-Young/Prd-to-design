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
2. `extract-prd-design-brief` reads the PRD and produces a structured design
   brief.
3. `produce-design-change-report` turns that brief into a polished HTML report.
4. If existing design context is needed, Codex reads Figma read-only when tools
   are available, or asks the user for screenshots.
5. Codex generates one UI concept image per key page by default.
6. The report is used to review affected screens, interaction changes,
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

## Skill 2: Produce Design Change Report

The HTML report should be a single, readable artifact with a Material Design 3
inspired structure. It should prioritize scanability and implementation clarity.

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
- Multimodal flow cards when the PRD describes a process.

## Visual Direction

- Use a calm, professional product design report style.
- Use MD3-style seed color tonal roles exposed as CSS variables.
- Use large rounded "memory card" surfaces for report sections and flow nodes.
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
