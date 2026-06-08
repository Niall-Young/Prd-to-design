#!/usr/bin/env python3
"""Render a PRD design change report as a static MD3-style HTML file."""

from __future__ import annotations

import argparse
import colorsys
import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_SEED = "#006A6A"
FLOW_NODE_TYPES = {
    "start": "开始",
    "process": "处理",
    "decision": "判断",
    "data": "数据",
    "end": "结束",
}


def esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_hex(value: Any) -> str:
    if not isinstance(value, str):
        return DEFAULT_SEED
    value = value.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.upper()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", value):
        return "#" + "".join(ch * 2 for ch in value[1:]).upper()
    return DEFAULT_SEED


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    raw = hex_color.lstrip("#")
    red = int(raw[0:2], 16) / 255
    green = int(raw[2:4], 16) / 255
    blue = int(raw[4:6], 16) / 255
    hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
    return hue * 360, saturation, lightness


def hsl_to_hex(hue: float, saturation: float, tone: float) -> str:
    red, green, blue = colorsys.hls_to_rgb((hue % 360) / 360, tone / 100, max(0, min(1, saturation)))
    return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"


def tonal_palette(seed: str) -> dict[str, str]:
    """Create MD3-style tonal role colors from a seed color.

    This is a lightweight dependency-free tonal generator. It follows MD3 role
    tone mapping and exposes stable CSS variables, while avoiding a heavyweight
    HCT/CAM16 dependency inside a local plugin.
    """

    hue, saturation, _ = hex_to_hsl(seed)
    primary_sat = max(0.42, min(0.82, saturation))
    secondary_sat = max(0.18, min(0.34, saturation * 0.55))
    tertiary_sat = max(0.24, min(0.48, saturation * 0.7))
    neutral_sat = 0.08
    neutral_variant_sat = 0.12

    def tone(kind: str, value: int) -> str:
        if kind == "primary":
            return hsl_to_hex(hue, primary_sat, value)
        if kind == "secondary":
            return hsl_to_hex(hue, secondary_sat, value)
        if kind == "tertiary":
            return hsl_to_hex(hue + 58, tertiary_sat, value)
        if kind == "neutral-variant":
            return hsl_to_hex(hue, neutral_variant_sat, value)
        if kind == "error":
            return hsl_to_hex(3, 0.72, value)
        return hsl_to_hex(hue, neutral_sat, value)

    return {
        "seed": seed,
        "primary": tone("primary", 40),
        "on-primary": tone("primary", 100),
        "primary-container": tone("primary", 90),
        "on-primary-container": tone("primary", 10),
        "secondary": tone("secondary", 40),
        "on-secondary": tone("secondary", 100),
        "secondary-container": tone("secondary", 90),
        "on-secondary-container": tone("secondary", 10),
        "tertiary": tone("tertiary", 40),
        "on-tertiary": tone("tertiary", 100),
        "tertiary-container": tone("tertiary", 90),
        "on-tertiary-container": tone("tertiary", 10),
        "surface": tone("neutral", 98),
        "on-surface": tone("neutral", 10),
        "surface-dim": tone("neutral", 87),
        "surface-container-low": tone("neutral", 96),
        "surface-container": tone("neutral", 94),
        "surface-container-high": tone("neutral", 92),
        "surface-container-highest": tone("neutral", 90),
        "outline": tone("neutral-variant", 50),
        "outline-variant": tone("neutral-variant", 80),
        "error": tone("error", 40),
        "on-error": tone("error", 100),
        "error-container": tone("error", 90),
        "on-error-container": tone("error", 10),
    }


def css_vars(colors: dict[str, str]) -> str:
    return "\n".join(f"    --md-sys-color-{name}: {value};" for name, value in colors.items())


def tag(label: Any, class_name: str = "") -> str:
    if not label:
        return ""
    extra = f" {class_name}" if class_name else ""
    return f'<span class="tag{extra}">{esc(label)}</span>'


def image_html(image: Any, alt: str = "") -> str:
    if not image:
        return ""
    src = None
    image_alt = alt
    source = None
    if isinstance(image, str):
        src = image
    elif isinstance(image, dict):
        src = image.get("path") or image.get("src") or image.get("image")
        image_alt = image.get("alt") or alt
        source = image.get("source")
    if not src:
        return ""
    source_chip = tag(source, "source") if source else ""
    return (
        '<figure class="media-card">'
        f'<img src="{esc(src)}" alt="{esc(image_alt)}" loading="lazy" />'
        f"{source_chip}"
        "</figure>"
    )


def list_items(items: Any) -> str:
    values = [item for item in as_list(items) if item not in (None, "")]
    if not values:
        return '<p class="muted">未提供</p>'
    rendered = []
    for item in values:
        if isinstance(item, dict):
            text = item.get("title") or item.get("name") or item.get("question") or item.get("description") or json.dumps(item, ensure_ascii=False)
            detail = item.get("description") or item.get("whyItMatters") or item.get("evidence")
            rendered.append(f"<li><strong>{esc(text)}</strong>{f'<p>{esc(detail)}</p>' if detail and detail != text else ''}</li>")
        else:
            rendered.append(f"<li>{esc(item)}</li>")
    return "<ul>" + "".join(rendered) + "</ul>"


def section(title: str, body: str, eyebrow: str | None = None) -> str:
    eyebrow_html = f'<div class="eyebrow">{esc(eyebrow)}</div>' if eyebrow else ""
    return f'<section class="memory-card">{eyebrow_html}<h2>{esc(title)}</h2>{body}</section>'


def render_context(context: Any) -> str:
    if not isinstance(context, dict):
        return list_items(context)
    source = context.get("source")
    body = f'<div class="tag-row">{tag(source, "source")}</div>'
    body += '<div class="two-col">'
    body += '<div><h3>已确认观察</h3>' + list_items(context.get("findings")) + "</div>"
    body += '<div><h3>假设与限制</h3>' + list_items(context.get("assumptions")) + "</div>"
    body += "</div>"
    return body


def render_impact(matrix: Any) -> str:
    if not isinstance(matrix, dict):
        return list_items(matrix)
    labels = [("add", "新增"), ("change", "修改"), ("remove", "删除")]
    cards = []
    for key, label in labels:
        cards.append(f'<article class="mini-card"><h3>{label}</h3>{list_items(matrix.get(key))}</article>')
    return '<div class="three-col">' + "".join(cards) + "</div>"


def render_screens(screens: Any) -> str:
    cards = []
    for screen in as_list(screens):
        if isinstance(screen, str):
            cards.append(f'<article class="mini-card"><h3>{esc(screen)}</h3></article>')
            continue
        if not isinstance(screen, dict):
            continue
        chips = "".join(tag(value) for value in [screen.get("status"), *as_list(screen.get("states"))] if value)
        cards.append(
            '<article class="screen-card">'
            f'<div class="tag-row">{chips}</div>'
            f'<h3>{esc(screen.get("name") or "未命名页面")}</h3>'
            f'<p>{esc(screen.get("summary") or screen.get("description") or "")}</p>'
            f'{image_html(screen.get("image"), screen.get("name") or "")}'
            f'<h4>设计动作</h4>{list_items(screen.get("designActions") or screen.get("actions"))}'
            "</article>"
        )
    if not cards:
        return '<p class="muted">未识别到页面级改动。</p>'
    return '<div class="screen-grid">' + "".join(cards) + "</div>"


def normalize_flow_node_type(value: Any, index: int, total: int) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in FLOW_NODE_TYPES:
            return normalized
    if index == 1:
        return "start"
    if index == total:
        return "end"
    return "process"


def render_flow_edges(edges: Any) -> str:
    pills = []
    for edge in as_list(edges):
        if not isinstance(edge, dict):
            continue
        start = edge.get("from")
        end = edge.get("to")
        if not start or not end:
            continue
        label = edge.get("label")
        label_html = f"<span>{esc(label)}</span>" if label else ""
        pills.append(
            '<span class="edge-pill">'
            f"<strong>{esc(start)} → {esc(end)}</strong>"
            f"{label_html}"
            "</span>"
        )
    if not pills:
        return ""
    return '<div class="flow-edges" aria-label="分支关系">' + "".join(pills) + "</div>"


def render_flows(flows: Any) -> str:
    rendered_flows = []
    for flow in as_list(flows):
        if not isinstance(flow, dict):
            continue
        raw_nodes = as_list(flow.get("nodes"))
        nodes = []
        total_nodes = len(raw_nodes)
        for index, node in enumerate(raw_nodes, start=1):
            if isinstance(node, str):
                node = {"title": node}
            if not isinstance(node, dict):
                continue
            node_type = normalize_flow_node_type(node.get("type") or node.get("shape"), index, total_nodes)
            node_id = node.get("id") or f"node-{index:02d}"
            type_label = FLOW_NODE_TYPES[node_type]
            chips = "".join(tag(value) for value in [type_label, node.get("status"), node.get("role"), node.get("screen")] if value)
            branch_label = node.get("branchLabel") or node.get("edgeLabel")
            branch_html = f'<div class="branch-label">{esc(branch_label)}</div>' if branch_label else ""
            nodes.append(
                '<li class="flow-step">'
                f"{branch_html}"
                f'<article class="flow-node is-{esc(node_type)}" data-node-id="{esc(node_id)}">'
                f'<div class="node-index">{index:02d}</div>'
                f'<div class="tag-row">{chips}</div>'
                f'<h3>{esc(node.get("title") or "未命名节点")}</h3>'
                f'<p>{esc(node.get("description") or "")}</p>'
                f'{image_html(node.get("image"), node.get("title") or "")}'
                f'<div class="node-action"><strong>设计动作</strong><span>{esc(node.get("designAction") or "待确认")}</span></div>'
                f'<p class="evidence">{esc(node.get("evidence") or "")}</p>'
                "</article>"
                "</li>"
            )
        if not nodes:
            continue
        meta = "".join(tag(value) for value in [flow.get("trigger"), flow.get("goal")] if value)
        rendered_flows.append(
            '<article class="flow-diagram-card">'
            f'<div class="flow-head"><div><h3>{esc(flow.get("name") or "未命名流程")}</h3></div><div class="tag-row">{meta}</div></div>'
            f'<ol class="flow-diagram" aria-label="{esc(flow.get("name") or "流程图")}">{"".join(nodes)}</ol>'
            f'{render_flow_edges(flow.get("edges"))}'
            "</article>"
        )
    if not rendered_flows:
        return '<p class="muted">PRD 未提供明确流程，报告未生成流程图。</p>'
    return "".join(rendered_flows)


def render_concepts(concepts: Any) -> str:
    cards = []
    for concept in as_list(concepts):
        if isinstance(concept, str):
            concept = {"title": concept}
        if not isinstance(concept, dict):
            continue
        cards.append(
            '<article class="concept-card">'
            f'{image_html(concept.get("image"), concept.get("title") or "")}'
            f'<div class="tag-row">{tag(concept.get("screen"))}</div>'
            f'<h3>{esc(concept.get("title") or "UI 概念图")}</h3>'
            f'<p>{esc(concept.get("prompt") or "")}</p>'
            f'{list_items(concept.get("notes"))}'
            "</article>"
        )
    if not cards:
        return '<p class="muted">尚未生成 UI 概念图。</p>'
    return '<div class="concept-grid">' + "".join(cards) + "</div>"


def render_report(report: dict[str, Any]) -> str:
    project_name = report.get("projectName") or report.get("title") or "PRD 设计变更报告"
    generated_at = report.get("generatedAt") or dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    seed = normalize_hex(report.get("seedColor"))
    seed_source = report.get("seedSource") or ("default" if seed == DEFAULT_SEED else "input")
    colors = tonal_palette(seed)

    body = []
    summary = report.get("summary") or "基于 PRD 提取设计改动，并整理为可评审的设计变更报告。"
    body.append(section("摘要", f"<p>{esc(summary)}</p>", "Overview"))
    body.append(section("当前设计现状", render_context(report.get("currentDesignContext")), "Context"))
    body.append(section("设计目标", list_items(report.get("goals")), "Goals"))
    body.append(section("新增 / 修改 / 删除", render_impact(report.get("impactMatrix")), "Impact"))
    body.append(section("页面级改动", render_screens(report.get("screens")), "Screens"))
    body.append(section("流程图", render_flows(report.get("flows")), "Flows"))
    body.append(section("UI 概念图", render_concepts(report.get("generatedConcepts")), "Generated UI"))
    body.append(section("组件 / 内容 / 状态需求", list_items(report.get("requirements")), "Requirements"))
    body.append(section("风险", list_items(report.get("risks")), "Risks"))
    body.append(section("开放问题", list_items(report.get("openQuestions")), "Questions"))
    body.append(section("下一步", list_items(report.get("nextActions")), "Next"))

    style = f"""
  :root {{
{css_vars(colors)}
    --card-radius: 28px;
    --card-radius-lg: 32px;
    --shadow-soft: 0 18px 48px rgba(0, 0, 0, .08);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    color: var(--md-sys-color-on-surface);
    background: var(--md-sys-color-surface);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.65;
  }}
  .page {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }}
  header.report-header {{
    display: grid;
    gap: 18px;
    margin-bottom: 24px;
    padding: 28px;
    border-radius: var(--card-radius-lg);
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    box-shadow: var(--shadow-soft);
  }}
  h1, h2, h3, h4, p {{ overflow-wrap: anywhere; }}
  h1 {{ margin: 0; font-size: clamp(2rem, 4vw, 4rem); line-height: 1.05; letter-spacing: 0; }}
  h2 {{ margin: 0 0 16px; font-size: 1.35rem; letter-spacing: 0; }}
  h3 {{ margin: 0 0 10px; font-size: 1rem; letter-spacing: 0; }}
  h4 {{ margin: 18px 0 8px; font-size: .9rem; color: var(--md-sys-color-secondary); }}
  p {{ margin: 0 0 12px; }}
  ul {{ margin: 0; padding-left: 1.1rem; }}
  li + li {{ margin-top: 8px; }}
  .meta-row, .tag-row {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .tag {{
    display: inline-flex;
    align-items: center;
    max-width: 100%;
    min-height: 30px;
    padding: 5px 11px;
    border-radius: 999px;
    background: var(--md-sys-color-secondary-container);
    color: var(--md-sys-color-on-secondary-container);
    font-size: .78rem;
    font-weight: 650;
    overflow-wrap: anywhere;
  }}
  .tag.source {{ background: var(--md-sys-color-tertiary-container); color: var(--md-sys-color-on-tertiary-container); }}
  .eyebrow {{ margin-bottom: 8px; color: var(--md-sys-color-primary); font-size: .78rem; font-weight: 750; text-transform: uppercase; letter-spacing: .08em; }}
  .memory-card, .mini-card, .screen-card, .concept-card, .flow-diagram-card, .flow-node {{
    border: 1px solid var(--md-sys-color-outline-variant);
    border-radius: var(--card-radius);
    background: var(--md-sys-color-surface-container);
    box-shadow: 0 8px 24px rgba(0, 0, 0, .045);
  }}
  .memory-card {{ padding: 24px; margin-top: 18px; }}
  .mini-card, .screen-card, .concept-card {{ padding: 18px; }}
  .two-col, .three-col, .screen-grid, .concept-grid {{ display: grid; gap: 14px; }}
  .two-col {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .three-col {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .screen-grid, .concept-grid {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
  .media-card {{ position: relative; margin: 12px 0; overflow: hidden; border-radius: 20px; background: var(--md-sys-color-surface-container-high); }}
  .media-card img {{ display: block; width: 100%; max-height: 360px; object-fit: cover; }}
  .media-card .tag {{ position: absolute; left: 10px; bottom: 10px; backdrop-filter: blur(8px); }}
  .flow-diagram-card {{ padding: 18px; background: var(--md-sys-color-surface-container-low); }}
  .flow-diagram-card + .flow-diagram-card {{ margin-top: 16px; }}
  .flow-head {{ display: flex; justify-content: space-between; gap: 12px; margin-bottom: 16px; }}
  .flow-diagram {{
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: minmax(250px, 1fr);
    gap: 54px;
    list-style: none;
    margin: 0;
    overflow-x: auto;
    padding: 4px 4px 14px;
  }}
  .flow-step {{ position: relative; display: grid; min-width: 250px; }}
  .flow-step:not(:last-child)::after {{
    content: "";
    position: absolute;
    left: calc(100% + 10px);
    top: 50%;
    width: 34px;
    border-top: 2px solid var(--md-sys-color-primary);
  }}
  .flow-step:not(:last-child)::before {{
    content: "";
    position: absolute;
    left: calc(100% + 36px);
    top: calc(50% - 5px);
    width: 10px;
    height: 10px;
    border-top: 2px solid var(--md-sys-color-primary);
    border-right: 2px solid var(--md-sys-color-primary);
    transform: rotate(45deg);
    z-index: 1;
  }}
  .flow-node {{ position: relative; min-width: 0; min-height: 100%; padding: 18px; background: var(--md-sys-color-surface-container-high); }}
  .flow-node.is-start, .flow-node.is-end {{ border-radius: 999px; align-content: center; }}
  .flow-node.is-decision {{
    border-style: dashed;
    background: var(--md-sys-color-tertiary-container);
    color: var(--md-sys-color-on-tertiary-container);
  }}
  .flow-node.is-data {{ background: var(--md-sys-color-secondary-container); color: var(--md-sys-color-on-secondary-container); }}
  .branch-label {{ justify-self: center; margin: 0 0 8px; padding: 3px 10px; border-radius: 999px; background: var(--md-sys-color-primary); color: var(--md-sys-color-on-primary); font-size: .74rem; font-weight: 800; }}
  .flow-edges {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
  .edge-pill {{ display: inline-grid; gap: 2px; padding: 8px 12px; border-radius: 16px; background: var(--md-sys-color-surface-container-highest); color: var(--md-sys-color-on-surface); font-size: .8rem; }}
  .node-index {{ color: var(--md-sys-color-primary); font-weight: 850; margin-bottom: 8px; }}
  .node-action {{ display: grid; gap: 4px; margin-top: 12px; padding: 12px; border-radius: 18px; background: var(--md-sys-color-primary-container); color: var(--md-sys-color-on-primary-container); }}
  .evidence, .muted {{ color: color-mix(in srgb, var(--md-sys-color-on-surface) 68%, transparent); font-size: .9rem; }}
  footer {{ margin-top: 18px; color: color-mix(in srgb, var(--md-sys-color-on-surface) 62%, transparent); font-size: .86rem; text-align: center; }}
  @media (max-width: 760px) {{
    .page {{ width: min(100% - 20px, 680px); padding-top: 16px; }}
    header.report-header, .memory-card {{ padding: 18px; border-radius: 24px; }}
    .two-col, .three-col {{ grid-template-columns: 1fr; }}
    .flow-head {{ display: grid; }}
    .flow-diagram {{ grid-auto-flow: row; grid-auto-columns: unset; overflow-x: visible; gap: 34px; }}
    .flow-step:not(:last-child)::after {{ left: 50%; top: calc(100% + 6px); width: 0; height: 22px; border-top: 0; border-left: 2px solid var(--md-sys-color-primary); }}
    .flow-step:not(:last-child)::before {{ left: calc(50% - 5px); top: calc(100% + 22px); transform: rotate(135deg); }}
  }}
"""

    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(project_name)} - 设计变更报告</title>
  <style>{style}</style>
</head>
<body>
  <main class="page">
    <header class="report-header">
      <div class="meta-row">
        {tag("PRD to Design")}
        {tag(f"Seed {seed}", "source")}
        {tag(f"配色来源: {seed_source}", "source")}
      </div>
      <h1>{esc(project_name)}</h1>
      <p>设计变更报告 · 生成时间 {esc(generated_at)}</p>
    </header>
    {''.join(body)}
    <footer>Generated by PRD to Design. HTML uses MD3-style tonal CSS variables and CSS-rendered flowchart diagrams.</footer>
  </main>
</body>
</html>
"""
    return html_doc


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an MD3-style design change report HTML.")
    parser.add_argument("--input", required=True, help="Report JSON path.")
    parser.add_argument("--output", required=True, help="Output HTML path.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if output_path.suffix.lower() not in {".html", ".htm"}:
        raise SystemExit("Output path must end in .html or .htm; Markdown outputs are not supported.")
    report = json.loads(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(report), encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
