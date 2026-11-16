"""Tests for the storyline-level checks in validate_storyline.py.

Each case mutates the (clean) sample storyline and asserts that a specific
message appears at a specific severity.

Usage (from anywhere): python evals/mbb-deck/test_validate_storyline.py [skill dir]
"""
import copy
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[2] / "plugins" / "mbb-deck-plugin" / "skills" / "mbb-deck"
skill = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
validator = skill / "scripts" / "validate_storyline.py"
base = json.loads(io.open(skill / "examples" / "sample-storyline.json", encoding="utf-8").read())


def run(story):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "case-storyline.json"
        f.write_text(json.dumps(story, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, str(validator), str(f)],
                           capture_output=True, text=True, encoding="utf-8",
                           env={"PYTHONIOENCODING": "utf-8", "SYSTEMROOT": "C:\\Windows"})
        return r.returncode, r.stdout + r.stderr


def idx(story, stype):
    return next(i for i, s in enumerate(story["slides"]) if s["type"] == stype)


cases = []


def case(name, severity, needle, exit_code=0):
    def deco(fn):
        cases.append((name, severity, needle, exit_code, fn))
        return fn
    return deco


@case("clean sample", None, "no issues found")
def _(s):
    pass


@case("unknown document_type", "ERROR", "unknown document_type", 1)
def _(s):
    s["meta"]["document_type"] = "strategy"


@case("missing document_type", "INFO", "meta.document_type")
def _(s):
    del s["meta"]["document_type"]


@case("board deck without decisions slide", "WARNING", "should close with a 'decisions' slide")
def _(s):
    del s["slides"][idx(s, "decisions")]
    del s["slides"][1]["decisions"]


@case("decisions slide not last before appendix", "INFO", "not the last page before the appendix")
def _(s):
    i = idx(s, "decisions")
    s["slides"].insert(i - 1, s["slides"].pop(i))


@case("pre-read with too many pages", "WARNING", "pages after the executive summary")
def _(s):
    s["meta"]["document_type"] = "decision_pre_read"


@case("short pre-read is not a short deck", None, "no issues found")
def _(s):
    s["meta"]["document_type"] = "decision_pre_read"
    keep = [0, 1, idx(s, "comparison"), idx(s, "chart"), idx(s, "decisions")]
    # keep summary figures backed: move the dropped pages' numbers into the appendix
    appendix = [{"type": "section", "title": "Appendix"}] + [
        sl for i, sl in enumerate(s["slides"]) if i not in keep and sl["type"] not in ("section",)]
    s["slides"] = [s["slides"][i] for i in keep] + appendix


@case("short deck without type still warns", "WARNING", "content slides")
def _(s):
    del s["meta"]["document_type"]
    s["slides"] = s["slides"][:4]
    s["slides"][1]["supporting_points"] = s["slides"][1]["supporting_points"][:3]


@case("vague decision", "WARNING", "asks for a discussion, not a decision")
def _(s):
    s["slides"][idx(s, "decisions")]["decisions"][0]["decision"] = "Discuss the enterprise strategy"


@case("decisions without deadline or why_now", "WARNING", "neither a deadline nor 'why_now'")
def _(s):
    d = s["slides"][idx(s, "decisions")]
    del d["why_now"]
    for x in d["decisions"]:
        del x["deadline"]


@case("empty decisions slide", "ERROR", "needs at least one decision", 1)
def _(s):
    s["slides"][idx(s, "decisions")]["decisions"] = []


@case("decision without sentence", "ERROR", "object with a 'decision' sentence", 1)
def _(s):
    s["slides"][idx(s, "decisions")]["decisions"][1] = {"owner": "COO"}


@case("six decisions", "WARNING", "more than five on one level")
def _(s):
    d = s["slides"][idx(s, "decisions")]
    d["decisions"] = d["decisions"] * 2


@case("summary and decisions page disagree", "WARNING", "they must match")
def _(s):
    s["slides"][1]["decisions"] = s["slides"][1]["decisions"][:2]


@case("summary does not ask for the decisions", "INFO", "does not ask for the decisions")
def _(s):
    del s["slides"][1]["decisions"]


@case("summary figure on no page", "WARNING", "appear in the executive summary but on no other page")
def _(s):
    s["slides"][1]["supporting_points"][1] = "**The enterprise segment is $7.7B** and growing 18%"


@case("process title", "WARNING", "opens with a process statement")
def _(s):
    s["slides"][2]["title"] = "We analyzed Acme financials and competitor filings for two years"


@case("we recommend is not process", None, "no issues found")
def _(s):
    s["slides"][idx(s, "chart")]["title"] = (
        "We recommend enterprise expansion: it adds $40M ARR by end-2027 and sunsetting SMB frees $14M")


@case("filler wording", "WARNING", "filler wording ['robust']")
def _(s):
    s["slides"][2]["bullets"][0] += " — a robust result"


@case("leverage ratio is not filler", None, "no issues found")
def _(s):
    s["slides"][2]["bullets"][0] = s["slides"][2]["bullets"][0].replace(
        "flat against", "at a stable leverage ratio and flat against")


@case("exclamation mark", "WARNING", "exclamation mark")
def _(s):
    s["slides"][2]["bullets"][1] += "!"


@case("quote slide is exempt from language check", None, "no issues found")
def _(s):
    s["slides"][idx(s, "quote")]["quote"] += " It would truly unlock everything!"


@case("long context", "INFO", "context runs beyond two sentences")
def _(s):
    s["slides"][1]["context"] += " A third sentence. And a fourth."


@case("next step without task", "ERROR", "object with a 'task'", 1)
def _(s):
    s["slides"][idx(s, "decisions")]["next_steps"][0] = {"owner": "CTO"}


# --- optional structures: stakeholders, key figures, page names, callouts ---

@case("callout without text", "ERROR", "callout is an object with a 'text'", 1)
def _(s):
    s["slides"][2]["callout"] = {"label": "Note"}


@case("callout on a section divider", "WARNING", "no body to attach a callout to")
def _(s):
    s["slides"][idx(s, "section")]["callout"] = {"text": "Detail follows."}


@case("long callout", "INFO", "keep it to one or two lines")
def _(s):
    s["slides"][2]["callout"] = {"text": "word " * 60}


@case("duplicate page name", "WARNING", "is already used by")
def _(s):
    s["slides"][2]["name"] = "The Decisions Page"


@case("unknown ladder stage", "ERROR", "unknown current_stage", 1)
def _(s):
    s["meta"]["stakeholders"][0]["current_stage"] = "sceptical"


@case("unknown stakeholder role", "ERROR", "unknown role", 1)
def _(s):
    s["meta"]["stakeholders"][0]["role"] = "sponsor"


@case("target below current stage", "WARNING", "target_stage lies below current_stage")
def _(s):
    s["meta"]["stakeholders"][0].update(current_stage="acts", target_stage="aware")


@case("three steps on the ladder", "INFO", "has to move 3 steps")
def _(s):
    s["meta"]["stakeholders"][0].update(current_stage="aware", target_stage="acts")


@case("concern recorded, answered nowhere", "INFO", "no page answers")
def _(s):
    for sl in s["slides"]:
        sl.pop("callout", None)
        for d in sl.get("decisions", []) if sl["type"] == "decisions" else []:
            d.pop("safeguard", None)


@case("structured audience is optional", None, "no issues found")
def _(s):
    del s["meta"]["stakeholders"]
    del s["meta"]["key_figures"]


@case("key figure not fully defined", "WARNING", "is not fully defined")
def _(s):
    del s["meta"]["key_figures"][0]["reference"]


@case("key figure without value", "ERROR", "each key figure needs a 'value'", 1)
def _(s):
    del s["meta"]["key_figures"][1]["value"]


@case("key figure on no page", "WARNING", "appears on no page in this form")
def _(s):
    s["meta"]["key_figures"][1]["value"] = "USD 14 million"


@case("components do not add up", "WARNING", "components add up to 35, not 40")
def _(s):
    s["meta"]["key_figures"][0]["components"] = [
        {"name": "new logos", "value": "$26M"}, {"name": "expansion", "value": "$9M"}]


@case("components reconcile", None, "no issues found")
def _(s):
    s["meta"]["key_figures"][0]["components"] = [
        {"name": "new logos", "value": "$26M"}, {"name": "expansion", "value": "$14M"}]


failed = 0
for name, severity, needle, exit_code, mutate in cases:
    story = copy.deepcopy(base)
    mutate(story)
    code, out = run(story)
    lines = [l for l in out.splitlines() if needle in l]
    ok = bool(lines) and code == exit_code
    if ok and severity:
        ok = any(l.strip().startswith(f"[{severity:>7}]") for l in lines)
    print(("PASS" if ok else "FAIL") + f": {name}")
    if not ok:
        failed += 1
        print("   expected", severity, repr(needle), "exit", exit_code, "- got exit", code)
        print("   " + "\n   ".join(out.strip().splitlines()[:8]))
print("---")
print(f"{len(cases) - failed} passed, {failed} failed")
sys.exit(1 if failed else 0)
