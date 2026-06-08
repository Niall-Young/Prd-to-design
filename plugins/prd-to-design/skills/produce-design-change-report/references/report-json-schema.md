# Report JSON Schema

`render_design_change_report.py` accepts a flexible JSON object. Prefer this shape for reliable rendering.

```json
{
  "projectName": "string",
  "projectSlug": "string",
  "language": "zh-CN",
  "projectType": "zero_to_one | iteration",
  "source": {
    "prdPath": "string | null",
    "figmaUrl": "string | null"
  },
  "seedColor": "#006A6A",
  "seedSource": "figma | screenshot | prd | default",
  "summary": "string",
  "currentDesignContext": {
    "source": "figma | screenshot | none | mixed",
    "findings": ["string"],
    "assumptions": ["string"]
  },
  "goals": ["string"],
  "impactMatrix": {
    "add": ["string"],
    "change": ["string"],
    "remove": ["string"]
  },
  "screens": [
    {
      "name": "string",
      "status": "new | existing | changed | removed | unknown",
      "summary": "string",
      "designActions": ["string"],
      "states": ["string"],
      "image": "assets/generated/screen.png"
    }
  ],
  "flows": [
    {
      "name": "string",
      "trigger": "string",
      "goal": "string",
      "diagramType": "flowchart",
      "nodes": [
        {
          "id": "string",
          "type": "start | process | decision | data | end",
          "title": "string",
          "description": "string",
          "role": "string",
          "status": "new | existing | changed | removed | unknown",
          "screen": "string",
          "designAction": "string",
          "evidence": "string",
          "image": {
            "path": "assets/prd/node.png",
            "alt": "string",
            "source": "prd | figma | screenshot | generated"
          }
        }
      ],
      "edges": [
        {
          "from": "string",
          "to": "string",
          "label": "string | null"
        }
      ]
    }
  ],
  "generatedConcepts": [
    {
      "title": "string",
      "screen": "string",
      "prompt": "string",
      "image": "assets/generated/concept.png",
      "notes": ["string"]
    }
  ],
  "requirements": ["string"],
  "risks": ["string"],
  "openQuestions": ["string"],
  "nextActions": ["string"]
}
```

Notes:

- `seedColor` is optional. When absent, the renderer uses a stable default and labels the source as `default`.
- `projectType` must come from the user-confirmed design brief. If it is `iteration`, include the required Figma URL in `source.figmaUrl`.
- Do not create report JSON until the PRD has passed the user confirmation gate. Before confirmation, ask the project-type question and wait.
- Final reports must be rendered to `.html`; Markdown is not a valid final report format for this skill.
- Image paths should be relative to the HTML file location.
- Flow nodes are rendered as CSS flowchart nodes. Use `diagramType: "flowchart"` and add `edges[]` for branch or loop labels.
