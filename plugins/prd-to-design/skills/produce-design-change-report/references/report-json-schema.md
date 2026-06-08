# Report JSON Schema

`render_design_change_report.py` accepts a flexible JSON object. Prefer this shape for reliable rendering.

```json
{
  "projectName": "string",
  "projectSlug": "string",
  "language": "zh-CN",
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
      "nodes": [
        {
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
- Image paths should be relative to the HTML file location.
- Flow nodes are rendered as multimodal cards when `image.path` or `image` is present.
