#!/usr/bin/env python3
"""
validate_storyline.py — Mechanically check an MBB-style storyline JSON
against the rules in references/storyline.md and references/slide-patterns.md.

Usage:
    python validate_storyline.py <storyline.json> [--strict]

Exit codes:
    0 — no issues, or only warnings (in non-strict mode)
    1 — errors found (or warnings in --strict mode)
    2 — file not found / unparseable

Checks fall into three severities:
    ERROR    — violates a hard rule (missing required fields, invalid type)
    WARNING  — violates a strong convention (topic title, too many slides)
    INFO     — stylistic suggestion
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------
# Heuristics
# --------------------------------------------------------------------------

# Words/phrases that suggest a TOPIC title rather than an ACTION title
TOPIC_PREFIXES = [
    "overview of", "introduction to", "summary of", "analysis of",
    "review of", "look at", "deep dive", "discussion of",
]
TOPIC_NOUNS_ONLY = [
    "overview", "introduction", "summary", "agenda", "background",
    "context", "current state", "market overview", "company overview",
    "recommendation", "next steps", "appendix",
    "findings", "observations", "key takeaways", "results",
]

# A title that is just a noun phrase (no verb) is usually a topic title.
# This is a loose check: if no common verb appears, flag it.
COMMON_VERBS = re.compile(
    r"\b(is|are|was|were|has|have|had|will|should|must|can|could|"
    r"grew|grow|growing|grown|increased|increases|increase|"
    r"declined|decline|fell|falls|fall|rose|rise|rises|risen|"
    r"drives|drive|drove|driven|reduce|reduces|reduced|reducing|"
    r"requires|require|required|requiring|enables|enable|enabled|"
    r"recommend|recommends|recommended|"
    r"shows|show|shown|showed|"
    r"means|mean|meant|"
    r"costs|cost|"
    r"makes|make|made|making|"
    r"takes|take|took|taken|"
    r"lose|loses|lost|losing|"
    r"win|wins|won|winning|"
    r"need|needs|needed|"
    r"add|adds|added|adding|"
    r"deliver|delivers|delivered|delivering|"
    r"face|faces|faced|facing|"
    r"meet|meets|met|meeting|"
    r"score|scores|scored|scoring|"
    r"fall|falls|fell|fallen|"
    r"contribute|contributes|contributed|"
    r"depend|depends|depended|"
    r"capture|captures|captured|capturing|"
    r"expand|expands|expanded|expanding|"
    r"exit|exits|exited|exiting|"
    r"sunset|sunsets|sunsetting|"
    r"move|moves|moved|moving|"
    r"do|does|did|done|doing|"
    r"go|goes|went|gone|going|"
    r"span|spans|spanned|spanning|"
    r"cover|covers|covered|covering|"
    r"include|includes|included|including|"
    r"explain|explains|explained|"
    r"answer|answers|answered)\b",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# Issue model
# --------------------------------------------------------------------------

class Issue:
    def __init__(self, severity: str, location: str, message: str):
        self.severity = severity
        self.location = location
        self.message = message

    def __str__(self):
        return f"[{self.severity:>7}] {self.location}: {self.message}"


# --------------------------------------------------------------------------
# Validators
# --------------------------------------------------------------------------

def validate_meta(meta: dict, issues: list[Issue]):
    if not isinstance(meta, dict):
        issues.append(Issue("ERROR", "meta", "meta must be an object"))
        return
    if not meta.get("title"):
        issues.append(Issue("ERROR", "meta.title", "missing required field"))
    if not meta.get("governing_thought"):
        issues.append(Issue(
            "WARNING", "meta.governing_thought",
            "missing — every MBB deck should have a single-sentence governing thought captured in meta"
        ))
    palette = meta.get("palette")
    valid_palettes = ["navy", "red", "green", "neutral"]
    if palette and palette not in valid_palettes:
        issues.append(Issue("ERROR", "meta.palette",
                            f"unknown palette '{palette}'; choose from {valid_palettes}"))


def validate_action_title(title: str, location: str, issues: list[Issue]):
    if not title:
        issues.append(Issue("ERROR", location, "title is empty"))
        return
    t = title.strip()
    lower = t.lower()

    # Check 1: pure topic noun
    for noun in TOPIC_NOUNS_ONLY:
        if lower == noun or lower.rstrip(":").rstrip(".") == noun:
            issues.append(Issue(
                "WARNING", location,
                f"title '{t}' is a topic label, not an action title — rewrite as a complete sentence stating the takeaway"
            ))
            return

    # Check 2: starts with a topic prefix
    for prefix in TOPIC_PREFIXES:
        if lower.startswith(prefix):
            issues.append(Issue(
                "WARNING", location,
                f"title '{t}' starts with a topic phrase ('{prefix}...') — rewrite as a sentence stating the conclusion"
            ))
            return

    # Check 3: no recognizable verb
    if not COMMON_VERBS.search(t):
        issues.append(Issue(
            "INFO", location,
            f"title '{t}' has no common verb — verify it states a claim, not a topic"
        ))

    # Check 4: ends with a period (most action titles in MBB style do not)
    if t.endswith("."):
        issues.append(Issue(
            "INFO", location,
            f"title '{t}' ends with a period; action titles conventionally end without one"
        ))

    # Check 5: too short
    if len(t.split()) < 4:
        issues.append(Issue(
            "WARNING", location,
            f"title '{t}' is very short ({len(t.split())} words); action titles typically state a specific claim"
        ))

    # Check 6: too long
    if len(t.split()) > 25:
        issues.append(Issue(
            "WARNING", location,
            f"title '{t}' is long ({len(t.split())} words); aim for a single readable sentence"
        ))


def validate_slides(slides: list, issues: list[Issue]):
    if not isinstance(slides, list) or not slides:
        issues.append(Issue("ERROR", "slides", "slides must be a non-empty array"))
        return

    types = [s.get("type") for s in slides]

    # Count of pages (excluding title)
    page_count = sum(1 for t in types if t != "title")
    if page_count < 5:
        issues.append(Issue(
            "WARNING", "slides",
            f"only {page_count} content slides — most MBB decks have 8–15"
        ))
    if page_count > 20:
        issues.append(Issue(
            "WARNING", "slides",
            f"{page_count} content slides — most MBB decks stay under 15; consider moving content to the appendix"
        ))

    # Title slide should be first
    if types and types[0] != "title":
        issues.append(Issue(
            "WARNING", "slides[0]",
            "first slide is not a title slide"
        ))

    # Executive summary should appear in first 3 slides
    if "exec_summary" not in types[:3]:
        issues.append(Issue(
            "WARNING", "slides",
            "no exec_summary slide in the first 3 — the governing thought should appear up front"
        ))

    # No more than one exec_summary at the start
    exec_indices = [i for i, t in enumerate(types) if t == "exec_summary"]
    if len(exec_indices) > 1:
        issues.append(Issue(
            "INFO", "slides",
            f"multiple exec_summary slides at indices {exec_indices}; usually one is enough"
        ))

    # Per-slide validation
    for i, slide in enumerate(slides):
        loc = f"slides[{i}] (type={slide.get('type', '?')})"
        validate_slide(slide, loc, issues)


def validate_slide(slide: dict, loc: str, issues: list[Issue]):
    stype = slide.get("type")
    if not stype:
        issues.append(Issue("ERROR", loc, "missing 'type' field"))
        return

    valid_types = {
        "title", "exec_summary", "bullets", "two_by_two", "mece_buckets",
        "comparison", "quote", "value_chain", "roadmap", "section",
        "section_divider", "chart", "chart_placeholder",
    }
    if stype not in valid_types:
        issues.append(Issue("ERROR", loc, f"unknown slide type '{stype}'"))
        return

    # Title is required for all except title and quote
    if stype not in ("title", "quote") and not slide.get("title"):
        issues.append(Issue("ERROR", loc, "missing 'title' field"))
        return

    if stype not in ("title", "quote", "section", "section_divider"):
        validate_action_title(slide.get("title", ""), f"{loc}.title", issues)

    # Type-specific checks
    if stype == "exec_summary":
        pts = slide.get("supporting_points", [])
        if not isinstance(pts, list) or len(pts) < 3:
            issues.append(Issue(
                "WARNING", loc,
                f"exec_summary should have 3–5 supporting points; got {len(pts) if isinstance(pts, list) else 0}"
            ))
        if isinstance(pts, list) and len(pts) > 5:
            issues.append(Issue(
                "WARNING", loc,
                f"exec_summary has {len(pts)} supporting points; cap at 5"
            ))

    elif stype == "bullets":
        bullets = slide.get("bullets", [])
        if not isinstance(bullets, list) or len(bullets) < 2:
            issues.append(Issue(
                "WARNING", loc,
                "bullets slide should have at least 2 bullets"
            ))
        if isinstance(bullets, list) and len(bullets) > 5:
            issues.append(Issue(
                "WARNING", loc,
                f"{len(bullets)} bullets — cap at 5; if you need more, split into two slides"
            ))

    elif stype == "mece_buckets":
        buckets = slide.get("buckets", [])
        if not isinstance(buckets, list) or len(buckets) < 3:
            issues.append(Issue(
                "WARNING", loc,
                f"MECE bucket slide should have 3–5 buckets; got {len(buckets) if isinstance(buckets, list) else 0}"
            ))
        if isinstance(buckets, list) and len(buckets) > 5:
            issues.append(Issue(
                "WARNING", loc,
                f"{len(buckets)} buckets — cap at 5 for readability"
            ))

    elif stype == "comparison":
        options = slide.get("options", [])
        criteria = slide.get("criteria", [])
        recommended = slide.get("recommended", -1)
        if len(options) < 2 or len(options) > 4:
            issues.append(Issue(
                "WARNING", loc,
                f"comparison should have 2–4 options; got {len(options)}"
            ))
        if recommended < 0 or recommended >= len(options):
            issues.append(Issue(
                "WARNING", loc,
                "no 'recommended' option specified — comparison slides should lead to a recommendation"
            ))
        for j, c in enumerate(criteria):
            ratings = c.get("ratings", [])
            if len(ratings) != len(options):
                issues.append(Issue(
                    "ERROR", f"{loc}.criteria[{j}]",
                    f"ratings length {len(ratings)} does not match options length {len(options)}"
                ))

    elif stype == "two_by_two":
        items = slide.get("items", [])
        if len(items) < 2:
            issues.append(Issue(
                "WARNING", loc,
                "2x2 has fewer than 2 items"
            ))
        for j, item in enumerate(items):
            x, y = item.get("x"), item.get("y")
            if x is None or y is None:
                issues.append(Issue("ERROR", f"{loc}.items[{j}]",
                                    "missing x or y coordinate"))
            else:
                if not (0 <= x <= 1) or not (0 <= y <= 1):
                    issues.append(Issue("ERROR", f"{loc}.items[{j}]",
                                        f"x and y must be in [0, 1]; got x={x}, y={y}"))

    elif stype == "roadmap":
        phases = slide.get("phases", [])
        if len(phases) < 2 or len(phases) > 4:
            issues.append(Issue(
                "WARNING", loc,
                f"roadmap should have 2–4 phases; got {len(phases)}"
            ))
        for j, p in enumerate(phases):
            ms = p.get("milestones", [])
            if len(ms) > 5:
                issues.append(Issue(
                    "INFO", f"{loc}.phases[{j}]",
                    f"phase has {len(ms)} milestones; usually 2–4 reads better"
                ))

    elif stype == "value_chain":
        steps = slide.get("steps", [])
        if len(steps) < 3 or len(steps) > 6:
            issues.append(Issue(
                "INFO", loc,
                f"value chain has {len(steps)} steps; 3–6 is typical"
            ))

    # Source check for data slides
    if stype in ("bullets", "two_by_two", "comparison", "chart", "chart_placeholder"):
        if not slide.get("source"):
            issues.append(Issue(
                "INFO", loc,
                "no source — data and finding slides should cite sources"
            ))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Validate an MBB storyline JSON")
    p.add_argument("storyline", type=Path)
    p.add_argument("--strict", action="store_true",
                   help="Treat warnings as errors")
    args = p.parse_args()

    if not args.storyline.exists():
        print(f"ERROR: file not found: {args.storyline}", file=sys.stderr)
        sys.exit(2)

    try:
        story = json.loads(args.storyline.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)

    issues: list[Issue] = []
    validate_meta(story.get("meta", {}), issues)
    validate_slides(story.get("slides", []), issues)

    # Sort: ERROR first, WARNING, INFO
    order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    issues.sort(key=lambda i: order.get(i.severity, 99))

    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]
    infos = [i for i in issues if i.severity == "INFO"]

    if not issues:
        print(f"✓ {args.storyline}: no issues found")
        sys.exit(0)

    for issue in issues:
        print(issue)

    print()
    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info")

    if errors or (args.strict and warnings):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
