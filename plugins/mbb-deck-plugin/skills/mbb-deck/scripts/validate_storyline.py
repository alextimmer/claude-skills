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

The checks calibrate to meta.document_type (board, decision_pre_read,
recurring_update, ...): a four-page pre-read is not a short deck, and a senior
decision document must close with its decision needs.

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

# Document types: the storyline bar differs by what the document is for.
DOCUMENT_TYPES = {
    "team_alignment",     # thoughts on paper, no polish needed
    "recurring_update",   # jour fixe / weekly: consistent structure, clean pages
    "board",              # board and senior management: full rigor, stands alone
    "decision_pre_read",  # cover + executive summary + up to four pages
    "external",           # board-level rigor plus legal / PR review
    "documentation",      # may be wordy, must stand fully on its own
    "keynote",            # few memorable messages, presenter is the soundtrack
}
# Types that must close with decision needs and next steps.
SENIOR_TYPES = {"board", "decision_pre_read", "external"}
# Types where a handful of pages is the norm, not a defect.
SHORT_TYPES = {"team_alignment", "recurring_update", "decision_pre_read", "keynote"}
PRE_READ_MAX_PAGES = 4

# A title that opens with what the team DID is process, not content.
PROCESS_TITLE = re.compile(
    r"^\s*(we|i|the team|our team|the project team)\s+(have\s+|has\s+)?"
    r"(conducted|ran|performed|analy[sz]ed|interviewed|held|talked|spoke|met|"
    r"looked|reviewed|evaluated|assessed|examined|investigated|studied|"
    r"worked|created|built|prepared|gathered|collected|surveyed|benchmarked)\b",
    re.IGNORECASE,
)

# Stock words and intensifiers that say nothing specific.
FILLER = re.compile(
    r"\b(delve[sd]?|delving|leverag(?:es|ed|ing)|"
    r"leverage(?=\s+(?:our|the|its|their|existing|this|these)\b)|"
    r"comprehensive|compelling|robust|pivotal|seamless(?:ly)?|"
    r"holistic(?:ally)?|impactful|unlock(?:s|ed|ing)?|really|truly|"
    r"it is important to note)\b",
    re.IGNORECASE,
)

# A decision need that does not name a decision.
VAGUE_DECISION = re.compile(
    r"\b(discuss|discussion|talk about|think about|consider|align on|"
    r"exchange views|feedback on)\b",
    re.IGNORECASE,
)

SECTION_TYPES = {"section", "section_divider"}

# Commitment ladder: where a stakeholder stands and where they must get to.
LADDER = ["unaware", "aware", "understands", "buys_in", "acts"]
STAKEHOLDER_ROLES = {"decides", "influences", "informed"}

# What makes a figure defined: what is measured, against what, for which period.
FIGURE_DEFINITION = ("measure", "reference", "period")
FIRST_NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")

# Slide types that carry no callout (no body to attach it to).
NO_CALLOUT_TYPES = {"title", "quote", "section", "section_divider"}

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

def validate_stakeholders(stakeholders, issues: list[Issue]):
    """Optional structured audience. Checked only when present."""
    if stakeholders is None:
        return
    if not isinstance(stakeholders, list) or not stakeholders:
        issues.append(Issue("ERROR", "meta.stakeholders",
                            "must be a non-empty array when present"))
        return
    for i, st in enumerate(stakeholders):
        loc = f"meta.stakeholders[{i}]"
        if not isinstance(st, dict) or not st.get("name"):
            issues.append(Issue("ERROR", loc, "each stakeholder needs a 'name'"))
            continue
        role = st.get("role")
        if role and role not in STAKEHOLDER_ROLES:
            issues.append(Issue(
                "ERROR", loc,
                f"unknown role '{role}'; choose from {sorted(STAKEHOLDER_ROLES)}"))
        stages = {}
        for key in ("current_stage", "target_stage"):
            stage = st.get(key)
            if stage and stage not in LADDER:
                issues.append(Issue(
                    "ERROR", loc, f"unknown {key} '{stage}'; choose from {LADDER}"))
            elif stage:
                stages[key] = LADDER.index(stage)
        if len(stages) == 2:
            jump = stages["target_stage"] - stages["current_stage"]
            if jump < 0:
                issues.append(Issue(
                    "WARNING", loc,
                    "target_stage lies below current_stage on the commitment ladder"))
            elif jump > 2:
                issues.append(Issue(
                    "INFO", loc,
                    f"'{st['name']}' has to move {jump} steps on the commitment "
                    "ladder — check what one document and one meeting can achieve"))


def figure_number(text):
    m = FIRST_NUMBER.search(str(text))
    return float(m.group(0).replace(",", ".")) if m else None


def validate_key_figures(figures, issues: list[Issue]):
    """Optional definitions of the headline figures. Checked only when present."""
    if figures is None:
        return
    if not isinstance(figures, list) or not figures:
        issues.append(Issue("ERROR", "meta.key_figures",
                            "must be a non-empty array when present"))
        return
    for i, fig in enumerate(figures):
        loc = f"meta.key_figures[{i}]"
        if not isinstance(fig, dict) or not fig.get("value"):
            issues.append(Issue("ERROR", loc, "each key figure needs a 'value'"))
            continue
        label = fig.get("name") or fig["value"]
        missing = [k for k in FIGURE_DEFINITION if not fig.get(k)]
        if missing:
            issues.append(Issue(
                "WARNING", loc,
                f"figure '{label}' is not fully defined — missing {missing}: say "
                "what is measured, against which reference, for which period"))
        parts = fig.get("components")
        if parts is not None:
            if not isinstance(parts, list) or len(parts) < 2 or not all(
                    isinstance(c, dict) and c.get("value") for c in parts):
                issues.append(Issue(
                    "ERROR", f"{loc}.components",
                    "components is an array of at least two {name, value} objects"))
                continue
            total = figure_number(fig["value"])
            values = [figure_number(c["value"]) for c in parts]
            if total is not None and None not in values \
                    and abs(sum(values) - total) > 0.005 * max(abs(total), 1):
                issues.append(Issue(
                    "WARNING", f"{loc}.components",
                    f"components add up to {sum(values):g}, not {total:g} — "
                    f"'{label}' and its parts must reconcile"))


def validate_figure_use(meta: dict, slides: list, issues: list[Issue]):
    """A defined figure must appear in the document, written the same way."""
    figures = meta.get("key_figures")
    if not isinstance(figures, list):
        return
    text = json.dumps(slides, ensure_ascii=False)
    for i, fig in enumerate(figures):
        if not isinstance(fig, dict) or not fig.get("value"):
            continue
        if str(fig["value"]) not in text:
            issues.append(Issue(
                "WARNING", f"meta.key_figures[{i}]",
                f"'{fig['value']}' is defined as a key figure but appears on no "
                "page in this form — the same number is written identically "
                "everywhere"))


def validate_concerns(meta: dict, slides: list, issues: list[Issue]):
    """Recorded main concerns should be answered on a page."""
    stakeholders = meta.get("stakeholders")
    if not isinstance(stakeholders, list):
        return
    concerned = [st.get("name") for st in stakeholders
                 if isinstance(st, dict) and st.get("main_concern")]
    if not concerned:
        return
    answered = any(s.get("callout") for s in slides) or any(
        isinstance(d, dict) and d.get("safeguard")
        for s in slides if s.get("type") == "decisions"
        for d in (s.get("decisions") or []))
    if not answered:
        issues.append(Issue(
            "INFO", "meta.stakeholders",
            f"main concerns are recorded for {concerned} but no page answers "
            "one — use a callout on the relevant page or a safeguard on the "
            "decisions slide"))


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
    doc_type = meta.get("document_type")
    if not doc_type:
        issues.append(Issue(
            "INFO", "meta.document_type",
            f"not set — choose one of {sorted(DOCUMENT_TYPES)} so page-count and "
            "decision-needs checks calibrate to what the document is for"
        ))
    elif doc_type not in DOCUMENT_TYPES:
        issues.append(Issue(
            "ERROR", "meta.document_type",
            f"unknown document_type '{doc_type}'; choose from {sorted(DOCUMENT_TYPES)}"
        ))
    for field, why in (
        ("audience", "who decides and what is their main concern"),
        ("objective", "what the audience should do after reading"),
        ("question", "the one question the governing thought answers"),
    ):
        if not meta.get(field):
            issues.append(Issue(
                "INFO", f"meta.{field}",
                f"not set — capture {why} before building pages"
            ))
    validate_stakeholders(meta.get("stakeholders"), issues)
    validate_key_figures(meta.get("key_figures"), issues)
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

    # Check 2b: process narration (what the team did, not what it found)
    if PROCESS_TITLE.search(t):
        issues.append(Issue(
            "WARNING", location,
            f"title '{t}' opens with a process statement — state what the work "
            "showed, not what was done (content beats process)"
        ))

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

    # Check 7: likely exceeds two rendered lines (~65 chars/line at title size).
    # "Maximum 2 lines. Cut filler words until it fits." (Firm Learning rule)
    if len(t) > 130:
        issues.append(Issue(
            "WARNING", location,
            f"title is {len(t)} characters — likely renders beyond two lines; "
            "cut filler words until it fits (max 2 lines)"
        ))


# Numeric tokens like 23%, 1,412.84, 40, FY27 — used for title/body match.
NUM_TOKEN = re.compile(r"\d[\d.,]*%?")

# Slide types whose data lives OUTSIDE the JSON (rendered chart), so numbers
# in the title legitimately may not appear in the JSON body.
CHART_TYPES = {"chart", "chart_placeholder"}


def validate_title_numbers(slide: dict, loc: str, issues: list[Issue]):
    """Every number in the action title must appear, identically, in the body.

    (Firm Learning + our anti-pattern list; here made mechanical.) Skipped for
    chart slides — their data lives in the rendered chart, not the JSON.
    """
    stype = slide.get("type")
    # exec_summary is exempt: its title is the governing thought, whose numbers
    # are proven by the deck's later slides, not by the one-page summary body.
    if stype in CHART_TYPES or stype in (
        "title", "quote", "section", "section_divider", "exec_summary"
    ):
        return
    title = slide.get("title", "") or ""
    tokens = {t.rstrip(".,") for t in NUM_TOKEN.findall(title)}
    tokens.discard("")
    if not tokens:
        return
    body = {k: v for k, v in slide.items() if k not in ("title", "type")}
    body_text = json.dumps(body, ensure_ascii=False)
    missing = sorted(tok for tok in tokens if tok not in body_text)
    if missing:
        issues.append(Issue(
            "WARNING", loc,
            f"number(s) {missing} appear in the title but not in the slide body — "
            "every number in the title must appear, identically, in the body"
        ))


# Sub-bullet markers embedded in a flat bullet string.
SUB_BULLET_PREFIX = re.compile(r"^\s*[-•·]\s")

# Chart taxonomy: choose the chart from the comparison type of the MESSAGE.
# NOTE the deliberate omission of "pie" everywhere: pie charts are banned in
# this skill (the skill author's hard rule) — for components use a stacked
# column or a sorted bar chart.
COMPARISON_CHART_MAP = {
    "components": {"stacked_column", "stacked_bar", "100_stacked", "sorted_bar", "column", "bar"},
    "items": {"bar", "sorted_bar", "column", "waterfall"},
    "time_series": {"line", "column"},
    "distribution": {"column", "histogram", "line"},
    "correlation": {"scatter", "bubble", "paired_bar"},
}

PIE_MENTION = re.compile(r"\bpie\b|\bdoughnut\b|\bdonut\b", re.IGNORECASE)


def validate_chart_taxonomy(slide: dict, loc: str, issues: list[Issue]):
    """comparison_type / chart_type consistency + the pie ban."""
    ctype = slide.get("chart_type")
    comp = slide.get("comparison_type")

    if ctype and ctype.lower().replace(" ", "_") in ("pie", "doughnut", "donut", "pie_chart"):
        issues.append(Issue(
            "ERROR", loc,
            "pie charts are banned in this skill (the skill author's hard rule) — "
            "for a components/share-of-whole message use a stacked column or a sorted bar chart"
        ))
    if comp:
        if comp not in COMPARISON_CHART_MAP:
            issues.append(Issue(
                "ERROR", loc,
                f"unknown comparison_type '{comp}'; choose from {sorted(COMPARISON_CHART_MAP)}"
            ))
        elif ctype and ctype.lower().replace(" ", "_") not in COMPARISON_CHART_MAP[comp]:
            issues.append(Issue(
                "WARNING", loc,
                f"chart_type '{ctype}' does not fit comparison_type '{comp}' — "
                f"expected one of {sorted(COMPARISON_CHART_MAP[comp])}; "
                "choose the chart from the message's comparison type, not the data shape"
            ))
    for field in ("placeholder_text", "caption"):
        text = slide.get(field, "") or ""
        if PIE_MENTION.search(text):
            issues.append(Issue(
                "WARNING", f"{loc}.{field}",
                "mentions a pie/doughnut chart — pie charts are banned in this skill "
                "(the skill author's hard rule); use a stacked column or sorted bar instead"
            ))


NON_PROSE_KEYS = {"type", "source", "chart_type", "comparison_type"}


def iter_strings(obj):
    """Yield every prose string in a slide (skipping type/source/enum keys)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in NON_PROSE_KEYS:
                yield from iter_strings(v)


def validate_language(slide: dict, loc: str, issues: list[Issue]):
    """Stock filler and exclamation marks. Quotes are verbatim and exempt."""
    if slide.get("type") == "quote":
        return
    hits, bang = set(), False
    for text in iter_strings(slide):
        hits.update(m.group(0).lower() for m in FILLER.finditer(text))
        bang = bang or "!" in text
    if hits:
        issues.append(Issue(
            "WARNING", loc,
            f"filler wording {sorted(hits)} — replace each with the concrete "
            "point, number or decision"
        ))
    if bang:
        issues.append(Issue(
            "WARNING", loc,
            "exclamation mark — executive documents state the point without one"
        ))


def main_body(slides: list) -> list:
    """Slides before the appendix divider, without the cover."""
    out = []
    for s in slides:
        title = (s.get("title") or "").lower()
        if s.get("type") in SECTION_TYPES and ("appendix" in title or "backup" in title):
            break
        if s.get("type") != "title":
            out.append(s)
    return out


def validate_summary_numbers(slides: list, issues: list[Issue]):
    """Executive summary drift: its figures must reappear in the document."""
    idx = next((i for i, s in enumerate(slides)
                if s.get("type") == "exec_summary"), None)
    if idx is None:
        return
    summary = {k: v for k, v in slides[idx].items()
               if k not in ("type", "source", "framing_line")}
    tokens = {t.rstrip(".,") for t in
              NUM_TOKEN.findall(json.dumps(summary, ensure_ascii=False))}
    tokens.discard("")
    rest = json.dumps([s for i, s in enumerate(slides) if i != idx],
                      ensure_ascii=False)
    missing = sorted(tok for tok in tokens if tok not in rest)
    if missing:
        has_chart = any(s.get("type") in CHART_TYPES for s in slides)
        issues.append(Issue(
            "WARNING", f"slides[{idx}] (type=exec_summary)",
            f"figure(s) {missing} appear in the executive summary but on no "
            "other page — the same number must be identical everywhere"
            + (" (ignore if it lives only inside a rendered chart)" if has_chart else "")
        ))


def validate_close(slides: list, doc_type, issues: list[Issue]):
    """Senior documents end on decision needs, then next steps."""
    body = main_body(slides)
    decision_idx = [i for i, s in enumerate(body) if s.get("type") == "decisions"]
    summary = next((s for s in slides if s.get("type") == "exec_summary"), None)

    if doc_type in SENIOR_TYPES:
        if not decision_idx:
            issues.append(Issue(
                "WARNING", "slides",
                f"a '{doc_type}' document should close with a 'decisions' slide "
                "(which decisions, by when, why now) followed by next steps — "
                "not with a data page"
            ))
        elif decision_idx[-1] != len(body) - 1:
            issues.append(Issue(
                "INFO", "slides",
                "the 'decisions' slide is not the last page before the appendix — "
                "the document should end on what is asked of the reader"
            ))

    if decision_idx and summary is not None:
        asked = summary.get("decisions")
        on_page = body[decision_idx[-1]].get("decisions", [])
        if not asked:
            issues.append(Issue(
                "INFO", "slides",
                "the executive summary does not ask for the decisions — it should "
                "name them ('decisions' field); the last page repeats them"
            ))
        elif isinstance(asked, list) and isinstance(on_page, list) \
                and len(asked) != len(on_page):
            issues.append(Issue(
                "WARNING", "slides",
                f"the executive summary asks for {len(asked)} decision(s) but the "
                f"decisions slide lists {len(on_page)} — they must match"
            ))


def validate_slides(slides: list, issues: list[Issue], meta: dict | None = None):
    if not isinstance(slides, list) or not slides:
        issues.append(Issue("ERROR", "slides", "slides must be a non-empty array"))
        return

    meta = meta if isinstance(meta, dict) else {}
    doc_type = meta.get("document_type")
    types = [s.get("type") for s in slides]

    # Count of pages (excluding title)
    page_count = sum(1 for t in types if t != "title")
    if page_count < 5 and doc_type not in SHORT_TYPES:
        issues.append(Issue(
            "WARNING", "slides",
            f"only {page_count} content slides — most MBB decks have 8–15 "
            "(set meta.document_type if this is a pre-read or a recurring update)"
        ))
    if doc_type == "decision_pre_read":
        pages = [s for s in main_body(slides) if s.get("type") != "exec_summary"]
        if len(pages) > PRE_READ_MAX_PAGES:
            issues.append(Issue(
                "WARNING", "slides",
                f"{len(pages)} pages after the executive summary — a decision "
                f"pre-read is cover, executive summary and up to "
                f"{PRE_READ_MAX_PAGES} pages; move the rest to the appendix"
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

    validate_close(slides, doc_type, issues)
    validate_summary_numbers(slides, issues)
    validate_figure_use(meta, slides, issues)
    validate_concerns(meta, slides, issues)

    # Page names are references ("the savings page"): they must be unique
    seen: dict = {}
    for i, s in enumerate(slides):
        name = s.get("name")
        if not name:
            continue
        key = str(name).strip().lower()
        if key in seen:
            issues.append(Issue(
                "WARNING", f"slides[{i}].name",
                f"page name '{name}' is already used by slides[{seen[key]}] — "
                "names must be unique to work as references"))
        else:
            seen[key] = i

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
        "section_divider", "chart", "chart_placeholder", "decisions",
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

        context = slide.get("context", "") or ""
        if len(re.findall(r"[.!?](?:\s|$)", context)) > 2:
            issues.append(Issue(
                "INFO", f"{loc}.context",
                "context runs beyond two sentences — situation and complication "
                "fit in two; the summary's space belongs to the arguments"
            ))
        asked = slide.get("decisions")
        if asked is not None and (not isinstance(asked, list) or not asked):
            issues.append(Issue(
                "ERROR", f"{loc}.decisions",
                "decisions must be a non-empty array of one-line decisions"
            ))
        elif asked and not slide.get("why_now"):
            issues.append(Issue(
                "INFO", f"{loc}.why_now",
                "decisions without 'why_now' — name the deadline that forces them"
            ))

    elif stype == "decisions":
        decisions = slide.get("decisions", [])
        if not isinstance(decisions, list) or not decisions:
            issues.append(Issue(
                "ERROR", f"{loc}.decisions",
                "a decisions slide needs at least one decision"
            ))
            decisions = []
        if len(decisions) > 5:
            issues.append(Issue(
                "WARNING", loc,
                f"{len(decisions)} decisions — more than five on one level is too "
                "many; group them or decide what this meeting can realistically settle"
            ))
        no_owner = 0
        any_deadline = False
        for j, d in enumerate(decisions):
            text = d.get("decision") if isinstance(d, dict) else None
            if not text:
                issues.append(Issue(
                    "ERROR", f"{loc}.decisions[{j}]",
                    "each decision is an object with a 'decision' sentence"
                ))
                continue
            if VAGUE_DECISION.search(text):
                issues.append(Issue(
                    "WARNING", f"{loc}.decisions[{j}]",
                    f"'{text}' asks for a discussion, not a decision — state what "
                    "is to be approved, chosen or released"
                ))
            no_owner += 0 if d.get("owner") else 1
            any_deadline = any_deadline or bool(d.get("deadline"))
        if decisions and not any_deadline and not slide.get("why_now"):
            issues.append(Issue(
                "WARNING", loc,
                "decision needs carry neither a deadline nor 'why_now' — say by "
                "when each decision is needed and what forces that date"
            ))
        elif decisions and not slide.get("why_now"):
            issues.append(Issue(
                "INFO", f"{loc}.why_now",
                "no 'why_now' — name the deadline that forces the decisions"
            ))
        if no_owner:
            issues.append(Issue(
                "INFO", loc,
                f"{no_owner} decision(s) without an owner"
            ))
        steps = slide.get("next_steps", [])
        if not steps:
            issues.append(Issue(
                "INFO", f"{loc}.next_steps",
                "no next steps — close with task, owner and date"
            ))
        loose = 0
        for j, st in enumerate(steps if isinstance(steps, list) else []):
            if not isinstance(st, dict) or not st.get("task"):
                issues.append(Issue(
                    "ERROR", f"{loc}.next_steps[{j}]",
                    "each next step is an object with a 'task'"
                ))
            elif not (st.get("owner") and st.get("date")):
                loose += 1
        if loose:
            issues.append(Issue(
                "INFO", f"{loc}.next_steps",
                f"{loose} next step(s) without owner or date"
            ))

    elif stype == "bullets":
        bullets = slide.get("bullets", [])
        if isinstance(bullets, list) and len(bullets) == 1:
            issues.append(Issue(
                "WARNING", loc,
                "a single bullet is not a list — write it as plain text instead "
                "(bullets always come in groups of at least 2)"
            ))
        elif not isinstance(bullets, list) or len(bullets) < 2:
            issues.append(Issue(
                "WARNING", loc,
                "bullets slide should have at least 2 bullets"
            ))
        if isinstance(bullets, list) and len(bullets) == 5:
            issues.append(Issue(
                "INFO", loc,
                "5 parallel bullets — consider grouping into labeled element groups "
                "(3 groups of 2 beat 1 list of 6; no clotheslines)"
            ))
        if isinstance(bullets, list) and len(bullets) > 5:
            issues.append(Issue(
                "WARNING", loc,
                f"{len(bullets)} bullets is a clothesline — group them into labeled "
                "element groups or split into two slides (cap: 5)"
            ))
        if isinstance(bullets, list):
            for j, b in enumerate(bullets):
                if not isinstance(b, str):
                    continue
                if len(b) > 160:
                    issues.append(Issue(
                        "WARNING", f"{loc}.bullets[{j}]",
                        f"bullet is {len(b)} characters — one idea per bullet, "
                        "one line ideally, two lines maximum"
                    ))
                if SUB_BULLET_PREFIX.match(b):
                    issues.append(Issue(
                        "INFO", f"{loc}.bullets[{j}]",
                        "bullet embeds a sub-bullet marker — use at most one level "
                        "of sub-bullets, or split the slide"
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

    # Numbers in the title must appear in the body (mechanical check)
    validate_title_numbers(slide, loc, issues)

    # Chart taxonomy + pie ban
    if stype in CHART_TYPES:
        validate_chart_taxonomy(slide, loc, issues)

    # Callout: one short box answering a concern or stating a caveat
    callout = slide.get("callout")
    if callout is not None:
        text = callout.get("text") if isinstance(callout, dict) else None
        if not text:
            issues.append(Issue(
                "ERROR", f"{loc}.callout",
                "callout is an object with a 'text' (and an optional 'label')"))
        elif stype in NO_CALLOUT_TYPES:
            issues.append(Issue(
                "WARNING", f"{loc}.callout",
                f"a '{stype}' slide has no body to attach a callout to — it is "
                "not rendered"))
        elif len(text) > 240:
            issues.append(Issue(
                "INFO", f"{loc}.callout",
                f"callout is {len(text)} characters — keep it to one or two "
                "lines; a longer answer deserves its own page"))

    # Filler wording and exclamation marks
    validate_language(slide, loc, issues)

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
        story = json.loads(args.storyline.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)

    issues: list[Issue] = []
    validate_meta(story.get("meta", {}), issues)
    validate_slides(story.get("slides", []), issues, story.get("meta", {}))

    # Sort: ERROR first, WARNING, INFO
    order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    issues.sort(key=lambda i: order.get(i.severity, 99))

    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]
    infos = [i for i in issues if i.severity == "INFO"]

    if not issues:
        print(f"OK {args.storyline}: no issues found")
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
