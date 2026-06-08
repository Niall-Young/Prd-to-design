# Design Brief Schema

Use this shape when `$extract-prd-design-brief` finishes analyzing a Markdown PRD. The values can be Markdown or JSON, but keep the keys stable so `$produce-design-change-report` can consume them.

```json
{
  "projectName": "string",
  "projectSlug": "string",
  "language": "zh-CN",
  "projectType": "greenfield | iteration_with_design | iteration_no_design | unknown",
  "source": {
    "prdPath": "string | null",
    "figmaUrl": "string | null",
    "screenshots": ["string"],
    "assetManifest": "string | null"
  },
  "targetUsers": [
    {
      "name": "string",
      "needs": ["string"],
      "evidence": "string"
    }
  ],
  "goals": [
    {
      "title": "string",
      "metric": "string | null",
      "evidence": "string"
    }
  ],
  "screens": [
    {
      "name": "string",
      "status": "new | existing | changed | removed | unknown",
      "designActions": ["string"],
      "states": ["default", "empty", "loading", "error"],
      "contentRequirements": ["string"],
      "dataRequirements": ["string"],
      "priority": "high | medium | low | unspecified",
      "evidence": "string"
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
          "role": "string | null",
          "status": "new | existing | changed | removed | unknown",
          "screen": "string | null",
          "designAction": "string",
          "evidence": "string",
          "image": {
            "path": "assets/prd/example.png",
            "alt": "string",
            "source": "prd | figma | screenshot | generated"
          }
        }
      ]
    }
  ],
  "requirements": [
    {
      "type": "add | change | remove | unknown",
      "title": "string",
      "description": "string",
      "affectedScreens": ["string"],
      "priority": "high | medium | low | unspecified",
      "evidence": "string"
    }
  ],
  "openQuestions": [
    {
      "question": "string",
      "whyItMatters": "string",
      "blocks": "string"
    }
  ]
}
```

Rules:

- Keep evidence short, preferably the PRD heading plus a short quote or paraphrase.
- Do not invent project type. Use `unknown` if the PRD does not establish it.
- Attach PRD images to the nearest useful screen or flow node. If uncertain, still keep the asset in `source.assetManifest` and mention uncertainty.
