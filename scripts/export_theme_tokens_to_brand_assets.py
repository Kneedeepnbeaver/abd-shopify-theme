"""
Export design tokens (colors, fonts, backgrounds) from abd-themes.css
into design/brand_assets for use in Photoshop and design tools.

Usage:
  python export_theme_tokens_to_brand_assets.py
  python export_theme_tokens_to_brand_assets.py --css path/to/abd-themes.css --out path/to/design/brand_assets
"""

import re
import os
import json
import csv
import struct
import argparse
from pathlib import Path


# Default paths (repo-relative from this script: frontend/theme/scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
DEFAULT_CSS = REPO_ROOT / "frontend" / "theme" / "assets" / "abd-themes.css"
DEFAULT_OUT = REPO_ROOT / "design" / "brand_assets"

# Core tokens we always try to resolve for the spec
CORE_COLOR_NAMES = ("ink", "paper", "muted", "accent", "rule")
FONT_NAMES = ("font-body", "font-headline", "font-heading")

# Hex normalization
HEX_SHORT = re.compile(r"^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$")
HEX_6 = re.compile(r"^#([0-9a-fA-F]{6})$")
HEX_8 = re.compile(r"^#([0-9a-fA-F]{8})$")


def normalize_hex(s):
    """Normalize hex to 6- or 8-digit lowercase."""
    s = s.strip()
    m = HEX_SHORT.match(s)
    if m:
        r, g, b = m.group(1), m.group(2), m.group(3)
        return f"#{r}{r}{g}{g}{b}{b}".lower()
    if HEX_6.match(s) or HEX_8.match(s):
        return s.lower()
    return s


def is_hex(s):
    return bool(re.match(r"^#[0-9a-fA-F]{3,8}$", s.strip()))


def is_rgba(s):
    return s.strip().startswith("rgba(") or s.strip().startswith("rgb(")


def is_color_literal(s):
    return is_hex(s) or is_rgba(s)


def parse_var_value(val):
    """Parse var(--name) or var(--name, fallback). Returns (name, fallback) or None."""
    val = val.strip()
    m = re.match(r"var\s*\(\s*--([a-zA-Z0-9-]+)\s*(?:,\s*(.+))?\)\s*$", val)
    if m:
        name = m.group(1)
        fallback = m.group(2).strip() if m.group(2) else None
        return (name, fallback)
    return None


def resolve_var(ref_name, theme_vars, visited=None):
    """Resolve a variable by name. Returns resolved string or None if unresolved."""
    if visited is None:
        visited = set()
    if ref_name in visited:
        return None
    visited.add(ref_name)
    raw = theme_vars.get(ref_name)
    if raw is None:
        return None
    raw = raw.strip()
    parsed = parse_var_value(raw)
    if parsed is None:
        if is_color_literal(raw):
            return normalize_hex(raw) if is_hex(raw) else raw
        return raw  # e.g. font string
    inner_name, fallback = parsed
    resolved = resolve_var(inner_name, theme_vars, visited)
    if resolved is not None:
        return resolved
    if fallback:
        fallback_parsed = parse_var_value(fallback)
        if fallback_parsed:
            res = resolve_var(fallback_parsed[0], theme_vars, set())
            if res is not None:
                return res
        if is_color_literal(fallback):
            return normalize_hex(fallback) if is_hex(fallback) else fallback
        return fallback
    return None


def extract_theme_blocks(content):
    """Find all .abd-theme-<id> { ... } blocks. Returns list of (theme_id, block_content, preceding_comment)."""
    blocks = []
    # Match .abd-theme-<id> { and then balance braces
    pattern = re.compile(r"\.abd-theme-([a-zA-Z0-9-]+)\s*\{", re.MULTILINE)
    pos = 0
    while True:
        m = pattern.search(content, pos)
        if not m:
            break
        theme_id = m.group(1)
        start = m.end()
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
            i += 1
        block_content = content[start : i - 1]
        # Preceding comment: /* --- something.css --- */
        comment_start = content.rfind("/* --- ", 0, m.start())
        preceding_comment = ""
        if comment_start >= 0:
            end_comment = content.find("*/", comment_start)
            if end_comment > comment_start:
                preceding_comment = content[comment_start : end_comment + 2]
        blocks.append((theme_id, block_content, preceding_comment))
        pos = i
    return blocks


def extract_declarations(block_content):
    """Extract --name: value; and background: value; from block. Returns (vars_dict, background_str)."""
    vars_dict = {}
    background_str = None
    # Root-level only: content before first nested { (so we don't grab background from nested rules)
    first_brace = block_content.find("{")
    root_section = block_content[: first_brace] if first_brace >= 0 else block_content
    # Match --name: value; (value may span lines and contain parens)
    for m in re.finditer(r"--([a-zA-Z0-9-]+)\s*:\s*([^;]+);", block_content, re.DOTALL):
        name = m.group(1)
        value = m.group(2).strip()
        vars_dict[name] = value
    # Root-level background only
    bg_m = re.search(r"^\s*background\s*:\s*([^;]+);", root_section, re.MULTILINE | re.DOTALL)
    if bg_m:
        background_str = bg_m.group(1).strip()
    return vars_dict, background_str


def humanize_theme_id(theme_id):
    """e.g. california-mission -> California Mission."""
    return theme_id.replace("-", " ").title()


def theme_name_from_comment(comment):
    """Extract filename from /* --- filename.css --- */ and humanize."""
    m = re.search(r"---\s*([^\s-]+)(?:\.css)?\s*---", comment)
    if m:
        return m.group(1).replace("-", " ").title()
    return None


def collect_all_theme_data(css_path):
    """Parse CSS and return list of theme dicts with merged vars and resolved colors."""
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_theme_blocks(content)
    # Merge by theme_id: later block wins per variable
    theme_blocks = {}
    for theme_id, block_content, preceding_comment in blocks:
        if theme_id not in theme_blocks:
            theme_blocks[theme_id] = {"vars": {}, "background": None, "comment": preceding_comment}
        decls, bg = extract_declarations(block_content)
        theme_blocks[theme_id]["vars"].update(decls)
        if bg:
            theme_blocks[theme_id]["background"] = bg

    themes_out = []
    for theme_id, data in theme_blocks.items():
        vars_map = data["vars"]
        if not vars_map:
            continue

        name = theme_name_from_comment(data["comment"]) or humanize_theme_id(theme_id)

        # Resolve core colors and build full palette (only color-like values)
        colors = {}
        palette = {}
        for var_name, raw in vars_map.items():
            parsed = parse_var_value(raw)
            if parsed:
                resolved = resolve_var(parsed[0], vars_map)
                if resolved and (is_hex(resolved) or is_rgba(resolved)):
                    palette[var_name] = resolved
                    if var_name in CORE_COLOR_NAMES:
                        colors[var_name] = resolved
            else:
                if is_color_literal(raw):
                    val = normalize_hex(raw) if is_hex(raw) else raw
                    palette[var_name] = val
                    if var_name in CORE_COLOR_NAMES:
                        colors[var_name] = val

        fonts = {}
        for fn in FONT_NAMES:
            if fn in vars_map:
                v = vars_map[fn].strip()
                if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                    v = v[1:-1]
                fonts[fn.replace("font-", "")] = v

        if "headline" not in fonts and "font-heading" in vars_map:
            v = vars_map["font-heading"].strip()
            if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                v = v[1:-1]
            fonts["headline"] = v

        theme_spec = {
            "id": theme_id,
            "name": name,
            "colors": colors,
            "palette": palette,
            "fonts": fonts,
            "background": data["background"],
        }
        if colors or palette or fonts:
            themes_out.append(theme_spec)

    return themes_out


def write_spec(themes, out_path):
    """Write abd-themes-spec.json."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"themes": themes}, f, indent=2)


def write_palette_csv(themes, palettes_dir):
    """Write one CSV per theme: token,hex (hex-only for Photoshop swatch reference)."""
    palettes_dir = Path(palettes_dir)
    palettes_dir.mkdir(parents=True, exist_ok=True)
    for t in themes:
        rows = []
        for token, value in t.get("palette", {}).items():
            if is_hex(value):
                rows.append((token, value))
        if not rows:
            continue
        path = palettes_dir / f"{t['id']}-colors.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(("token", "hex"))
            w.writerows(rows)


def _hex_to_rgb(hex_str):
    """Convert #rrggbb to (r, g, b) floats in 0-1."""
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        return None
    try:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return (r, g, b)
    except ValueError:
        return None


def _build_ase_file(colors):
    """
    Build Adobe Swatch Exchange (.ase) binary from list of (name, hex) tuples.
    ASE uses big-endian; names are UTF-16 BE; RGB as three Float32 (0-1).
    """
    # Header: signature + version 1.0 + block count (group start + N colors + group end)
    block_count = len(colors) + 2
    buf = bytearray()
    buf.extend(b"ASEF")
    buf.extend(struct.pack(">HH", 1, 0))  # version 1.0
    buf.extend(struct.pack(">I", block_count))

    # Group start (0xc001): optional group name
    group_name = "Palette"
    name_utf16 = group_name.encode("utf-16-be")
    name_len_chars = len(group_name)
    group_block_len = 2 + len(name_utf16)
    buf.extend(struct.pack(">H", 0xC001))
    buf.extend(struct.pack(">I", group_block_len))
    buf.extend(struct.pack(">H", name_len_chars))
    buf.extend(name_utf16)

    # Color blocks (0x0001)
    for name, hex_val in colors:
        rgb = _hex_to_rgb(hex_val)
        if rgb is None:
            continue
        # Sanitize name for ASE (no nulls; truncate if very long)
        name = (name or "swatch").replace("\x00", "")[:256]
        name_utf16 = name.encode("utf-16-be")
        name_len_chars = len(name)
        block_len = 2 + len(name_utf16) + 4 + 12 + 2  # name len + name + "RGB " + 3 floats + type
        buf.extend(struct.pack(">H", 0x0001))
        buf.extend(struct.pack(">I", block_len))
        buf.extend(struct.pack(">H", name_len_chars))
        buf.extend(name_utf16)
        buf.extend(b"RGB ")
        buf.extend(struct.pack(">fff", rgb[0], rgb[1], rgb[2]))
        buf.extend(struct.pack(">H", 0))  # 0 = Global color type

    # Group end (0xc002)
    buf.extend(struct.pack(">H", 0xC002))
    buf.extend(struct.pack(">I", 0))

    return bytes(buf)


def write_palette_ase(themes, palettes_dir):
    """Write one Adobe Swatch Exchange (.ase) file per theme for loading in Photoshop."""
    palettes_dir = Path(palettes_dir)
    palettes_dir.mkdir(parents=True, exist_ok=True)
    for t in themes:
        colors = []
        for token, value in t.get("palette", {}).items():
            if is_hex(value):
                colors.append((token, value))
        if not colors:
            continue
        ase_bytes = _build_ase_file(colors)
        path = palettes_dir / f"{t['id']}.ase"
        with open(path, "wb") as f:
            f.write(ase_bytes)


def main():
    parser = argparse.ArgumentParser(description="Export theme tokens from abd-themes.css to brand_assets")
    parser.add_argument("--css", type=Path, default=DEFAULT_CSS, help="Path to abd-themes.css")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Path to design/brand_assets")
    args = parser.parse_args()

    if not args.css.exists():
        print(f"Error: CSS file not found: {args.css}")
        return 1

    themes = collect_all_theme_data(args.css)
    print(f"Found {len(themes)} themes with design tokens")

    write_spec(themes, args.out / "abd-themes-spec.json")
    print(f"Wrote {args.out / 'abd-themes-spec.json'}")

    write_palette_csv(themes, args.out / "palettes")
    print(f"Wrote CSV palettes to {args.out / 'palettes'}")

    write_palette_ase(themes, args.out / "palettes")
    print(f"Wrote ASE swatch files to {args.out / 'palettes'}")

    return 0


if __name__ == "__main__":
    exit(main() or 0)
