#!/usr/bin/env python3
"""
lint_prose.py — Mechanically check an executive summary, memo or email draft
against the parts of the storyline standard a machine can measure.

Usage:
    python lint_prose.py <draft.md|draft.txt> [--type summary|email|memo] [--strict]
    python lint_prose.py - < draft.txt          # read from stdin

Exit codes:
    0 — no issues, or only warnings/info (non-strict)
    1 — warnings found in --strict mode
    2 — file not found / unreadable

Checks:
    filler      stock words, stock phrases and empty intensifiers
    emphasis    exclamation marks
    process     sentences that report activity ("we conducted ...")
    vague       unquantified claims ("significant upside")
    trailing    trailing participle clauses (", ensuring ...")
    sprawl      more than five parallel top-level bullets
    numbers     no figure anywhere in the draft
    ask         no decision or next step named (summary / email / memo)
    opening     the draft opens with process or pleasantries (email)

This lint measures wording and shape. Whether the governing thought is right,
the arguments are MECE and the numbers are true still needs a reader.
Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FILLER = re.compile(
    r"\b(delve[sd]?|delving|leverag(?:es|ed|ing)|"
    r"leverage(?=\s+(?:our|the|its|their|existing|this|these)\b)|"
    r"comprehensive|compelling|robust|pivotal|seamless(?:ly)?|"
    r"holistic(?:ally)?|impactful|unlock(?:s|ed|ing)?|really|truly|"
    r"it is important to note|it is worth noting|here is why|"
    r"what makes it work|at the end of the day|"
    r"not all \w+ are created equal)\b",
    re.IGNORECASE,
)

PROCESS = re.compile(
    r"^\W*(we|i|the team|our team|the project team)\s+(have\s+|has\s+|also\s+)?"
    r"(conducted|ran|performed|analy[sz]ed|interviewed|held|talked|spoke|met|"
    r"looked|reviewed|evaluated|assessed|examined|investigated|studied|"
    r"worked|created|built|prepared|gathered|collected|surveyed|benchmarked|"
    r"started|continued|rebuilt|visited)\b",
    re.IGNORECASE,
)

VAGUE = re.compile(
    r"\b(significant|substantial|considerable|major|huge|strong|meaningful)\s+"
    r"(upside|potential|savings|impact|improvement|growth|benefits?|"
    r"opportunit(?:y|ies)|synergies|value)\b",
    re.IGNORECASE,
)

TRAILING = re.compile(
    r",\s+(ensuring|enabling|allowing|aiming to|helping|driving|"
    r"positioning|paving the way)\b",
    re.IGNORECASE,
)

PLEASANTRY = re.compile(
    r"^\W*(i hope|hope this|as discussed|as you know|further to|following up|"
    r"i wanted to|just wanted|we would like to share|please find)\b",
    re.IGNORECASE,
)

ASK = re.compile(
    r"\b(decision|decide|approve|approval|release|sign[- ]?off|next steps?|"
    r"we need|you need to|by when)\b",
    re.IGNORECASE,
)

HAS_NUMBER = re.compile(r"\d")
BULLET = re.compile(r"^([-*•]|\d+[.)])\s+")
SENTENCE_SPLIT = re.compile(r"(?<=[.?!])\s+")


class Issue:
    def __init__(self, severity, check, message):
        self.severity, self.check, self.message = severity, check, message

    def __str__(self):
        return f"[{self.severity:>7}] {self.check}: {self.message}"


def clean_lines(text: str) -> list[str]:
    """Drop code fences; strip quote markers and markdown emphasis."""
    out, fenced = [], False
    for raw in text.splitlines():
        if raw.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        line = re.sub(r"^\s*>+\s?", "", raw)
        out.append(line.replace("**", "").replace("__", ""))
    return out


def lint(text: str, doc_type: str, issues: list) -> None:
    lines = clean_lines(text)
    body = [l for l in lines if l.strip() and not l.lstrip().startswith("#")]
    if not body:
        issues.append(Issue("WARNING", "empty", "no text to check"))
        return
    whole = "\n".join(body)

    hits = sorted({m.group(0).lower() for m in FILLER.finditer(whole)})
    if hits:
        issues.append(Issue(
            "WARNING", "filler",
            f"{hits} — replace each with the concrete point, number or decision"
        ))

    if "!" in whole:
        issues.append(Issue(
            "WARNING", "emphasis",
            "exclamation mark — state the point without one"
        ))

    for line in body:
        stripped = BULLET.sub("", line.strip())
        for sentence in SENTENCE_SPLIT.split(stripped):
            if PROCESS.search(sentence):
                issues.append(Issue(
                    "WARNING", "process",
                    f"\"{sentence.strip()[:70]}\" reports activity — say what it "
                    "showed, or move it to one next-steps line"
                ))

    for m in VAGUE.finditer(whole):
        issues.append(Issue(
            "INFO", "vague",
            f"\"{m.group(0)}\" — quantify it (value, baseline, period)"
        ))

    for m in TRAILING.finditer(whole):
        issues.append(Issue(
            "INFO", "trailing",
            f"trailing clause \"{m.group(0).strip(', ')}...\" — make it its own "
            "statement or cut it"
        ))

    # Longest run of consecutive top-level bullets
    run = longest = 0
    for line in lines:
        if BULLET.match(line):          # top level only: no leading indent
            run += 1
            longest = max(longest, run)
        elif line.strip() and not line.startswith((" ", "\t")):
            run = 0
    if longest > 5:
        issues.append(Issue(
            "WARNING", "sprawl",
            f"{longest} parallel bullets in one list — more than five on a "
            "level is too many; group them into three"
        ))

    if not HAS_NUMBER.search(whole):
        issues.append(Issue(
            "INFO", "numbers",
            "no figure anywhere — quantify the arguments wherever the source "
            "allows (never invent a number)"
        ))

    if doc_type in ("summary", "email", "memo") and not ASK.search(whole):
        issues.append(Issue(
            "WARNING", "ask",
            "no decision or next step named — close with what is asked of the "
            "reader: which decisions, by when, why now"
        ))

    if doc_type == "email":
        opening = [l for l in body if not l.lower().startswith("subject:")]
        first = BULLET.sub("", opening[0].strip()) if opening else ""
        first = re.sub(r"^(dear|hi|hello)\b[^,\n]*,\s*", "", first, flags=re.I)
        if PLEASANTRY.search(first) or PROCESS.search(first):
            issues.append(Issue(
                "WARNING", "opening",
                f"opens with \"{first[:60]}\" — open with the context in one or "
                "two sentences, then the recommendation"
            ))


def main():
    p = argparse.ArgumentParser(
        description="Lint an executive summary, memo or email draft")
    p.add_argument("draft", help="path to a text/markdown file, or - for stdin")
    p.add_argument("--type", choices=["summary", "email", "memo", "other"],
                   default="summary", dest="doc_type")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 when warnings are found")
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.draft == "-":
        text = sys.stdin.read()
    else:
        path = Path(args.draft)
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        text = path.read_text(encoding="utf-8", errors="replace")

    issues: list = []
    lint(text, args.doc_type, issues)

    if not issues:
        print(f"OK {args.draft}: no issues found")
        sys.exit(0)

    order = {"WARNING": 0, "INFO": 1}
    issues.sort(key=lambda i: order.get(i.severity, 9))
    for issue in issues:
        print(issue)
    warnings = [i for i in issues if i.severity == "WARNING"]
    print()
    print(f"Summary: {len(warnings)} warnings, {len(issues) - len(warnings)} info")
    sys.exit(1 if (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
