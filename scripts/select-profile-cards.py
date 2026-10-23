#!/usr/bin/env python3
"""Keep only the two validated Summary Cards images used by the profile."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


OUTPUT = Path("profile-summary-card-output")
CARD = "0-profile-details.svg"
THEMES = ("default", "github_dark")
SVG_NS = "http://www.w3.org/2000/svg"
MAX_BYTES = 1_000_000
URL_REF = re.compile(r"url\(\s*(['\"]?)([^)]+?)\1\s*\)", re.IGNORECASE)
ROW_INDEX = re.compile(r"(?:^|;)\s*--gpsc-i:\s*(\d+)\s*(?:;|$)")


def normalize_metadata(root: ET.Element, path: Path, *, check_only: bool) -> None:
    """Remove upstream's optional email/company/location row, or reject drift."""
    panels = [
        elem
        for elem in root.iter(f"{{{SVG_NS}}}g")
        if elem.get("transform") == "translate(30,30)"
    ]
    if len(panels) != 1:
        raise ValueError(f"Unexpected profile-details panel: {path}")
    panel = panels[0]
    by_index: dict[int, list[ET.Element]] = {}
    for child in panel:
        if child.get("class") != "gpsc-item":
            raise ValueError(f"Unexpected profile-details row structure: {path}")
        match = ROW_INDEX.search(child.get("style", ""))
        if match is None:
            raise ValueError(f"Missing profile-details row index: {path}")
        index = int(match.group(1))
        if index not in {0, 1, 2, 3}:
            raise ValueError(f"Unexpected profile-details row index {index}: {path}")
        by_index.setdefault(index, []).append(child)

    def shape(index: int) -> set[str]:
        return {item.tag.rsplit("}", 1)[-1] for item in by_index.get(index, [])}

    for index in (0, 1, 2):
        if len(by_index.get(index, [])) != 2 or shape(index) != {"g", "text"}:
            raise ValueError(f"Missing or changed required row {index}: {path}")
    optional = by_index.get(3, [])
    if optional and (len(optional) != 2 or shape(3) != {"g", "text"}):
        raise ValueError(f"Changed optional metadata row: {path}")
    if check_only and optional:
        raise ValueError(f"Optional metadata row was not removed: {path}")
    for item in optional:
        panel.remove(item)


def validate_svg(path: Path, *, check_only: bool) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or unsafe card: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) > MAX_BYTES or b"<!DOCTYPE" in raw.upper():
        raise ValueError(f"Invalid SVG size or doctype: {path}")
    root = ET.fromstring(raw)
    if root.tag != f"{{{SVG_NS}}}svg" or root.get("width") != "700":
        raise ValueError(f"Unexpected SVG root or width: {path}")
    normalize_metadata(root, path, check_only=check_only)
    for elem in root.iter():
        local = elem.tag.rsplit("}", 1)[-1].lower()
        if local in {"script", "foreignobject", "iframe", "image", "a", "use"}:
            raise ValueError(f"Executable or external SVG element in {path}: {local}")
        for key, value in elem.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            if attr.startswith("on") or attr in {"href", "src"}:
                raise ValueError(f"Unsafe SVG attribute in {path}: {attr}")
            if "javascript:" in value.lower() or "@import" in value.lower():
                raise ValueError(f"Unsafe SVG value in {path}: {attr}")
            for match in URL_REF.finditer(value):
                if not match.group(2).strip("'\" ").startswith("#"):
                    raise ValueError(f"External SVG URL in {path}: {attr}")
        if local == "style":
            css = elem.text or ""
            if "@import" in css.lower():
                raise ValueError(f"External SVG stylesheet in {path}")
            for match in URL_REF.finditer(css):
                if not match.group(2).strip("'\" ").startswith("#"):
                    raise ValueError(f"External SVG CSS URL in {path}")
    text = " ".join(node.text or "" for node in root.iter())
    if "Public Repos" not in text or "Joined GitHub" not in text:
        raise ValueError(f"Card appears incomplete: {path}")
    if check_only:
        return raw
    ET.register_namespace("", SVG_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if OUTPUT.is_symlink() or not OUTPUT.is_dir():
        raise ValueError("Missing or unsafe generated output directory")
    cards = {theme: validate_svg(OUTPUT / theme / CARD, check_only=args.check_only) for theme in THEMES}
    if args.check_only:
        expected = {OUTPUT / theme / CARD for theme in THEMES}
        expected_dirs = {OUTPUT / theme for theme in THEMES}
        entries = set(OUTPUT.rglob("*"))
        if any(path.is_symlink() for path in entries):
            raise ValueError("Symlink in output tree")
        if entries != expected | expected_dirs:
            raise ValueError(f"Unexpected output entries: {sorted(entries - expected - expected_dirs)}")
        print("Validated default and github_dark profile-detail SVGs")
        return

    stage = Path(tempfile.mkdtemp(prefix="profile-cards-", dir="."))
    try:
        for theme, raw in cards.items():
            dest = stage / theme / CARD
            dest.parent.mkdir()
            dest.write_bytes(raw)
        shutil.rmtree(OUTPUT)
        stage.rename(OUTPUT)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print("Selected and validated default and github_dark profile-detail SVGs")


if __name__ == "__main__":
    main()
