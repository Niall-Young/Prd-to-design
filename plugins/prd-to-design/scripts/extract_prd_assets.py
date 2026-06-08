#!/usr/bin/env python3
"""Extract Markdown image references from a PRD and copy local assets."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse


IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def slugify(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or fallback


def split_markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    quoted = re.match(r"^([^\"']+?)\s+[\"'].*[\"']$", target)
    if quoted:
        return quoted.group(1).strip()
    return target.strip("\"'")


def is_remote(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme in {"http", "https", "data"}


def unique_destination(output_dir: Path, index: int, source: Path, alt: str) -> Path:
    suffix = source.suffix or mimetypes.guess_extension(mimetypes.guess_type(source.name)[0] or "") or ".asset"
    base = slugify(alt or source.stem, f"prd-image-{index:02d}")
    candidate = output_dir / f"{index:02d}-{base}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{index:02d}-{base}-{counter}{suffix}"
        counter += 1
    return candidate


def extract_assets(prd_path: Path, output_dir: Path) -> dict:
    markdown = prd_path.read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    prd_dir = prd_path.parent
    assets = []

    for index, match in enumerate(IMAGE_RE.finditer(markdown), start=1):
        alt = match.group(1).strip()
        target = split_markdown_target(match.group(2))
        decoded_target = unquote(target)
        asset = {
            "id": f"prd-image-{index:02d}",
            "alt": alt,
            "original": target,
            "markdown": match.group(0),
            "remote": is_remote(target),
            "exists": False,
            "copied": None,
            "relativeOutput": None,
            "mime": mimetypes.guess_type(target)[0],
        }

        if not asset["remote"]:
            source = Path(decoded_target)
            if not source.is_absolute():
                source = prd_dir / source
            source = source.resolve()
            asset["resolvedSource"] = str(source)

            if source.exists() and source.is_file():
                destination = unique_destination(output_dir, index, source, alt)
                shutil.copy2(source, destination)
                asset["exists"] = True
                asset["copied"] = str(destination)
                if output_dir.parent.name == "assets" and output_dir.parent.parent.exists():
                    asset["relativeOutput"] = str(destination.relative_to(output_dir.parent.parent))
                else:
                    asset["relativeOutput"] = str(destination.relative_to(output_dir.parent))
                asset["mime"] = mimetypes.guess_type(destination.name)[0]

        assets.append(asset)

    return {
        "source": str(prd_path),
        "outputDir": str(output_dir),
        "count": len(assets),
        "copiedCount": sum(1 for item in assets if item["copied"]),
        "assets": assets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Markdown PRD image assets.")
    parser.add_argument("--prd", required=True, help="Path to the Markdown PRD file.")
    parser.add_argument("--output-dir", required=True, help="Directory where copied assets are written.")
    parser.add_argument("--json", help="Optional path for the JSON asset manifest.")
    args = parser.parse_args()

    prd_path = Path(args.prd).expanduser().resolve()
    if not prd_path.exists():
        raise SystemExit(f"PRD file not found: {prd_path}")
    if prd_path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
        raise SystemExit("v1 supports Markdown PRD files only.")

    manifest = extract_assets(prd_path, Path(args.output_dir).expanduser().resolve())
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)

    if args.json:
        json_path = Path(args.json).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
