# HTML Style Spec

The report is a work artifact, not a landing page. Keep the layout clear, card-based, and easy to scan.

Visual rules:

- Use Material Design 3 style tonal roles generated from a seed color.
- Emit CSS variables for `primary`, `on-primary`, `primary-container`, `secondary`, `tertiary`, `surface`, `surface-container`, `surface-container-high`, `outline`, and `error`.
- Default card radius: 28px. Compact chips and thumbnails may use 16px-20px.
- Use soft surfaces, light shadows, and subtle outlines. Avoid strong gradients.
- Use independent "memory card" surfaces for summary, flow nodes, screens, concepts, risks, and questions.
- Use responsive grids. Desktop may use horizontal flow tracks; mobile must stack content vertically.
- Never let long text overflow cards. Use wrapping and sensible line heights.

Content rules:

- Report in Chinese by default.
- Separate PRD facts, Figma/screenshot observations, generated concepts, assumptions, and open questions.
- Every flow card node may include title, description, status tag, role tag, design action, evidence, and an image thumbnail.
