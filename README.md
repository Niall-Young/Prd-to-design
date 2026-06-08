<a id="top"></a>

<div align="center">
  <img src="plugins/prd-to-design/assets/prd-to-design-logo.png" alt="PRD to Design logo" width="96" />
  <h1>PRD to Design</h1>
  <p>Turn Markdown PRDs into confirmed design briefs and MD3-style HTML design change reports.</p>
  <p><a href="#中文">中文</a> | <a href="#english">English</a></p>
</div>

---

<a id="中文"></a>

## 中文

PRD to Design 是一个本地 Codex 插件脚手架，用于把 Markdown PRD 转换成可交付给产品、设计和工程团队审阅的设计产物。它强调先确认项目类型，再输出结构化设计简报和静态 HTML 设计变更报告，避免在 PRD 信息不足时擅自扩展产品范围。

### 核心能力

- 读取 Markdown PRD，并在继续分析前询问这是 `0-1` 新项目/新功能，还是现有项目上的迭代。
- 如果是迭代，必须先收集可访问的 Figma 链接，再生成设计简报或报告。
- 提取页面、流程、状态、组件、内容、数据、权限、风险和开放问题等设计相关信息。
- 将 PRD 图片资源复制到项目输出目录，并保留远程图片引用。
- 生成 `outputs/<project-slug>/report.json` 和 `outputs/<project-slug>/design-change-report.html`。
- 产出 Material Design 3 风格的响应式 HTML 报告，包含页面影响、组件状态、流程图、风险和后续设计动作。

### 插件结构

```text
plugins/prd-to-design/
  .codex-plugin/plugin.json
  assets/
  scripts/
    extract_prd_assets.py
    render_design_change_report.py
  skills/
    extract-prd-design-brief/
    produce-design-change-report/
design.md
```

### 工作流程

1. 用户提供 Markdown PRD 文件路径或粘贴的 Markdown PRD 内容。
2. `extract-prd-design-brief` 只确认 PRD 可读，然后停下来询问项目类型。
3. 用户确认 `0-1` 或 `迭代`；如果是迭代，需要同时提供 Figma 链接。
4. 插件提取设计相关信息，写入 `outputs/<project-slug>/design-brief.json`。
5. `produce-design-change-report` 生成报告 JSON，并渲染静态 HTML。
6. 用户通过 HTML 报告审阅影响页面、交互变化、组件需求、风险和开放问题。

### 辅助脚本

提取 PRD 中的图片资源：

```bash
python3 plugins/prd-to-design/scripts/extract_prd_assets.py \
  --prd path/to/prd.md \
  --output-dir outputs/<project-slug>/assets/prd \
  --json outputs/<project-slug>/prd-assets.json
```

渲染 HTML 设计变更报告：

```bash
python3 plugins/prd-to-design/scripts/render_design_change_report.py \
  --input outputs/<project-slug>/report.json \
  --output outputs/<project-slug>/design-change-report.html
```

### 输出原则

- 忠实保留 PRD 意图，不新增 PRD 中没有提出的页面、角色或工作流。
- 明确区分已确认需求、建议、假设和开放问题。
- 默认把设计分析写入 HTML 报告，而不是只在聊天里输出。
- 迭代类项目必须基于用户提供的 Figma 链接或导出的当前设计材料进行说明。
- 报告应便于审阅、移交和工程实现。

[Back to language switch](#top)

---

<a id="english"></a>

## English

PRD to Design is a local Codex plugin scaffold that turns Markdown PRDs into design-ready artifacts for product, design, and engineering review. It confirms the project type before analysis, then produces a structured design brief and a static HTML design change report without inventing product scope that is not present in the PRD.

### Core Capabilities

- Read Markdown PRDs and ask whether the work is `0-to-1` or an iteration before continuing.
- Require an accessible Figma link before producing briefs or reports for iteration work.
- Extract design-relevant pages, flows, states, components, content, data, permissions, risks, and open questions.
- Copy local PRD image assets into the project output folder while preserving remote image references.
- Generate `outputs/<project-slug>/report.json` and `outputs/<project-slug>/design-change-report.html`.
- Render responsive Material Design 3 inspired HTML reports with screen impact, component states, flowcharts, risks, and next design actions.

### Plugin Structure

```text
plugins/prd-to-design/
  .codex-plugin/plugin.json
  assets/
  scripts/
    extract_prd_assets.py
    render_design_change_report.py
  skills/
    extract-prd-design-brief/
    produce-design-change-report/
design.md
```

### Workflow

1. The user provides a Markdown PRD file path or pasted Markdown PRD content.
2. `extract-prd-design-brief` only verifies that the PRD is readable, then stops and asks for the project type.
3. The user confirms `0-to-1` or `iteration`; iterations must include a Figma link.
4. The plugin extracts design-relevant information and writes `outputs/<project-slug>/design-brief.json`.
5. `produce-design-change-report` creates the report JSON and renders a static HTML report.
6. The user reviews affected screens, interaction changes, component needs, risks, and open questions in the HTML report.

### Helper Scripts

Extract image assets from a PRD:

```bash
python3 plugins/prd-to-design/scripts/extract_prd_assets.py \
  --prd path/to/prd.md \
  --output-dir outputs/<project-slug>/assets/prd \
  --json outputs/<project-slug>/prd-assets.json
```

Render the HTML design change report:

```bash
python3 plugins/prd-to-design/scripts/render_design_change_report.py \
  --input outputs/<project-slug>/report.json \
  --output outputs/<project-slug>/design-change-report.html
```

### Output Principles

- Preserve PRD intent and avoid adding pages, roles, or workflows that are not requested.
- Separate confirmed requirements, recommendations, assumptions, and open questions.
- Put design analysis in the generated HTML report by default, not only in chat.
- For iteration work, describe the current design only from the provided Figma link or exported current-state materials.
- Keep reports easy to review, hand off, and implement.

[返回语言切换](#top)
