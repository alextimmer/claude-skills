#!/usr/bin/env python3
"""
lint_deck.py — Mechanically verify a finished .pptx against the MBB visual
rules that a machine can measure (references/visual-style.md is canonical).

Works on ANY .pptx regardless of what produced it: build_deck.py, claude.ai
file creation, the official pptx skill, or a hand-built deck. This is the
deterministic half of production QA — the qa-reviewer agent runs this first,
then spends its judgment only on what machines cannot score.

Usage:
    python lint_deck.py <deck.pptx> [--profile default|dense] [--strict]

Exit codes (same convention as validate_storyline.py):
    0 — no issues, or only warnings/info (non-strict)
    1 — errors found (or warnings in --strict mode)
    2 — file not found / not readable as pptx

Checks:
    fonts         one font family across the deck (explicitly-set names)
    sizes         body text converges on one size per slide (band by profile)
    colors        max 2 chromatic colors per slide (accent discipline);
                  grays/black/white are free
    bounds        no shape extends beyond the slide edges
    jitter        title tops and page-number positions identical across slides
    spaces        no double spaces in text
    pagenum       page number present on every slide except the first
    charts        NO pie/doughnut charts (hard ban), no 3D chart types
    fills         no gradient fills
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.enum.dml import MSO_FILL_TYPE
    from pptx.util import Emu
except ImportError:
    print("ERROR: python-pptx is required (pip install python-pptx). "
          "On claude.ai it is preinstalled.", file=sys.stderr)
    sys.exit(2)

# Typography bands (pt) per profile: (title_min, body_lo, body_hi, footnote_max)
PROFILES = {
    "default": {"title_min": 18, "body_lo": 10, "body_hi": 17, "footnote_max": 9},
    "dense":   {"title_min": 16, "body_lo": 8,  "body_hi": 11, "footnote_max": 8},
}

PIE_TYPES = set()
THREED_TYPES = set()
for name in dir(XL_CHART_TYPE):
    if "PIE" in name or "DOUGHNUT" in name:
        PIE_TYPES.add(getattr(XL_CHART_TYPE, name))
    if name.startswith("THREE_D"):
        THREED_TYPES.add(getattr(XL_CHART_TYPE, name))

PAGE_NUM_RE = re.compile(r"^\s*\d{1,3}\s*$")
LEADING_MARKER = re.compile(r"^[\s•·▪◦od*-]+")  # bullet glyphs
EMU_PER_IN = 914400


def inches(emu) -> float:
    return round(emu / EMU_PER_IN, 1)


class Issue:
    def __init__(self, severity, check, message):
        self.severity, self.check, self.message = severity, check, message

    def __str__(self):
        return f"[{self.severity:>7}] {self.check}: {self.message}"


def is_chromatic(rgb) -> bool:
    """True for colors that are not white/black/gray (channel spread > 16)."""
    r, g, b = rgb[0], rgb[1], rgb[2]
    return (max(r, g, b) - min(r, g, b)) > 16


def iter_runs(shape):
    if not shape.has_text_frame:
        return
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            yield run


def lint(path: Path, profile: str, issues: list) -> None:
    prs = Presentation(str(path))
    band = PROFILES[profile]
    slide_w, slide_h = prs.slide_width, prs.slide_height
    tol = Emu(9525)  # ~0.01 inch tolerance

    fonts_used = {}          # name -> first slide seen
    title_tops = {}          # rounded top (in) -> [slide numbers]
    pagenum_pos = {}         # rounded (left, top) -> [slide numbers]
    slides_missing_pagenum = []

    for idx, slide in enumerate(prs.slides, start=1):
        slide_sizes = set()
        slide_colors = set()
        has_pagenum = False

        for shape in slide.shapes:
            # -- bounds --------------------------------------------------
            if shape.left is not None and shape.top is not None:
                right = shape.left + (shape.width or 0)
                bottom = shape.top + (shape.height or 0)
                if (shape.left < -tol or shape.top < -tol
                        or right > slide_w + tol or bottom > slide_h + tol):
                    issues.append(Issue(
                        "WARNING", "bounds",
                        f"slide {idx}: shape '{shape.name}' extends beyond the slide edge"
                    ))

            # -- charts --------------------------------------------------
            if getattr(shape, "has_chart", False):
                ct = shape.chart.chart_type
                if ct in PIE_TYPES:
                    issues.append(Issue(
                        "ERROR", "charts",
                        f"slide {idx}: pie/doughnut chart — banned in this skill "
                        "(the skill author's hard rule); use a stacked column or sorted bar"
                    ))
                elif ct in THREED_TYPES:
                    issues.append(Issue(
                        "WARNING", "charts",
                        f"slide {idx}: 3D chart type {ct} — no 3D; rebuild flat"
                    ))

            # -- gradient fills -------------------------------------------
            try:
                if shape.fill.type == MSO_FILL_TYPE.GRADIENT:
                    issues.append(Issue(
                        "WARNING", "fills",
                        f"slide {idx}: shape '{shape.name}' uses a gradient fill — "
                        "flat fills only"
                    ))
                if shape.fill.type == MSO_FILL_TYPE.SOLID:
                    rgb = shape.fill.fore_color.rgb
                    if rgb is not None and is_chromatic(rgb):
                        slide_colors.add(str(rgb))
            except (TypeError, AttributeError, NotImplementedError):
                pass

            # -- text-level checks ----------------------------------------
            if shape.has_text_frame:
                whole_text = shape.text_frame.text or ""
                # Page numbers live in the footer zone only — a bare digit
                # anywhere else (numbered points, chart labels) doesn't count.
                in_footer_zone = (shape.top is not None
                                  and shape.top > slide_h * 0.85)
                if PAGE_NUM_RE.match(whole_text) and in_footer_zone:
                    has_pagenum = True
                    if shape.left is not None:
                        key = (inches(shape.left), inches(shape.top))
                        pagenum_pos.setdefault(key, []).append(idx)

                for para in shape.text_frame.paragraphs:
                    ptext = "".join(r.text for r in para.runs)
                    # strip a leading bullet glyph + its spacing before checking
                    body = LEADING_MARKER.sub("", ptext)
                    if re.search(r"\S  +\S", body):
                        issues.append(Issue(
                            "WARNING", "spaces",
                            f"slide {idx}: double space in \"{body.strip()[:50]}\""
                        ))

                for run in iter_runs(shape):
                    if run.font.name:
                        fonts_used.setdefault(run.font.name, idx)
                    if run.font.size is not None:
                        pt = run.font.size.pt
                        if band["body_lo"] <= pt <= band["body_hi"]:
                            slide_sizes.add(pt)
                        if pt >= band["title_min"] and shape.top is not None \
                                and shape.top < Emu(int(1.5 * EMU_PER_IN)):
                            title_tops.setdefault(
                                inches(shape.top), []).append(idx)
                    try:
                        rgb = run.font.color.rgb
                        if rgb is not None and is_chromatic(rgb):
                            slide_colors.add(str(rgb))
                    except (TypeError, AttributeError):
                        pass

        # -- per-slide verdicts -------------------------------------------
        if len(slide_sizes) > 2:
            issues.append(Issue(
                "WARNING", "sizes",
                f"slide {idx}: {len(slide_sizes)} distinct body text sizes "
                f"({sorted(slide_sizes)}) — one font size for all body text on a "
                "page; only the action title and footnotes differ"
            ))
        if len(slide_colors) > 2:
            issues.append(Issue(
                "WARNING", "colors",
                f"slide {idx}: {len(slide_colors)} chromatic colors in use "
                f"({sorted(slide_colors)}) — max three colors per slide "
                "(primary, accent, neutral); the accent highlights ONE thing"
            ))
        if idx > 1 and not has_pagenum:
            slides_missing_pagenum.append(idx)

    # -- deck-level verdicts ------------------------------------------------
    if len(fonts_used) > 1:
        listing = ", ".join(f"'{n}' (first on slide {s})" for n, s in fonts_used.items())
        issues.append(Issue(
            "WARNING", "fonts",
            f"{len(fonts_used)} font families in use: {listing} — one font "
            "family for the entire deck, no mixing"
        ))
    if slides_missing_pagenum:
        issues.append(Issue(
            "WARNING", "pagenum",
            f"no page number found on slide(s) {slides_missing_pagenum} — every "
            "slide except the title carries a page number bottom-right"
        ))
    if len(title_tops) > 1:
        detail = "; ".join(f"top={k}in on slides {v}" for k, v in sorted(title_tops.items()))
        issues.append(Issue(
            "WARNING", "jitter",
            f"title position varies across slides ({detail}) — recurring "
            "elements sit in identical positions slide to slide (no jittering)"
        ))
    if len(pagenum_pos) > 1:
        detail = "; ".join(f"{k}in on slides {v}" for k, v in sorted(pagenum_pos.items()))
        issues.append(Issue(
            "WARNING", "jitter",
            f"page-number position varies across slides ({detail})"
        ))


def main():
    p = argparse.ArgumentParser(description="Lint a finished .pptx against MBB visual rules")
    p.add_argument("deck", type=Path)
    p.add_argument("--profile", choices=sorted(PROFILES), default="default",
                   help="Typography profile to check against (see assets/style_config.json)")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = p.parse_args()

    if not args.deck.exists():
        print(f"ERROR: file not found: {args.deck}", file=sys.stderr)
        sys.exit(2)

    issues: list = []
    try:
        lint(args.deck, args.profile, issues)
    except Exception as e:  # not a pptx / corrupt
        print(f"ERROR: could not read as pptx: {e}", file=sys.stderr)
        sys.exit(2)

    order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    issues.sort(key=lambda i: order.get(i.severity, 99))
    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]

    if not issues:
        print(f"OK {args.deck}: no mechanical issues found "
              f"(profile={args.profile})")
        sys.exit(0)

    for issue in issues:
        print(issue)
    print()
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings "
          f"(profile={args.profile})")
    print("Note: this lint measures what machines can measure. Storyline "
          "quality, So-Whats, and chart-message fit still need the reviewer "
          "agents.")

    if errors or (args.strict and warnings):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
