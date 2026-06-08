# AGENTS.md

## Scope

These instructions apply to the entire repository.

This workspace contains a local Codex plugin scaffold for `prd-to-design`. The
plugin lives under `plugins/prd-to-design` and currently defines two skills:

- `extract-prd-design-brief`: extracts actionable design work from Markdown PRDs.
- `produce-design-change-report`: turns extracted design briefs into HTML design
  change reports.

## Working Principles

- Keep changes narrowly scoped to the plugin and its skills unless the user asks
  for broader repository work.
- Treat Markdown PRDs as the primary input format.
- Keep generated design outputs reviewable, deterministic, and easy to hand off.
- Do not invent product scope that is not present in the PRD. Flag missing
  information as open questions.
- Prefer structured sections and explicit acceptance criteria over loose prose.
- Keep skill instructions self-contained so Codex can use each skill without
  reading unrelated files.

## Repository Layout

- `plugins/prd-to-design/.codex-plugin/plugin.json`: plugin manifest.
- `plugins/prd-to-design/skills/*/SKILL.md`: skill entrypoints and workflows.
- `plugins/prd-to-design/skills/*/agents/openai.yaml`: agent-facing skill
  display metadata.
- `plugins/prd-to-design/scripts/`: shared deterministic helpers for PRD asset
  extraction and HTML report rendering.
- `.agents/plugins/marketplace.json`: local marketplace registration.
- `design.md`: product and output design direction for this plugin.

## Editing Guidelines

- When editing a skill, update both its front matter and its body so the
  description, trigger conditions, workflow, and output format agree.
- Keep skill names stable unless the plugin manifest and agent metadata are
  updated together.
- Use plain Markdown for instructions. Avoid hidden dependencies or references
  to files that do not exist.
- For HTML report guidance, prefer accessible, responsive, Material Design 3
  inspired structure rather than decorative one-off styling.
- If adding shared scripts, place them under `plugins/prd-to-design/scripts/`
  and document when to run them from the relevant skill.

## Validation

Before handing work back after repository edits:

- Run `git status --short` to confirm the changed files.
- Validate edited JSON with `python3 -m json.tool <file>` when JSON files change.
- Skim changed `SKILL.md` files to ensure there are no leftover scaffold placeholders.

There is no project-wide build or test command yet.
