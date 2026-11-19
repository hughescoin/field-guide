#!/usr/bin/env python3
"""Build field guide pages from content files and the shared template.

    python3 build.py guides/my-topic.json     # validate and build one guide
    python3 build.py --all                    # rebuild every guide in guides/
    python3 build.py --check guides/x.json    # validate only, write nothing

Output goes to dist/<slug>.html (override with -o DIR). Uses only the standard library.
The format is documented in reference/guide-format.md.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "template.html"
GUIDES = HERE / "guides"

HUES = {"amber", "magenta", "teal", "green", "blue", "violet", "ink"}
TONES = {"good", "risk", "neutral"}
SIDES = {"left", "right", "top", "bottom"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Required fields per section type (beyond "type").
SECTION_FIELDS = {
    "layers": ["title", "layers"],
    "profile": ["entity", "oneLiner", "analogy", "why", "terms", "watch"],
    "compare": ["title", "columns", "rows"],
    "simulator": ["title", "diagram", "scenarios"],
    "panels": ["title", "panels"],
    "beforeAfter": ["title", "before", "after"],
    "questions": ["title", "items"],
    "quiz": ["title", "questions"],
    "prose": ["title"],
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def _text_fields(obj, path=""):
    """Yield (path, string) for every string inside obj."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _text_fields(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _text_fields(v, f"{path}[{i}]")


def validate(g: dict) -> Report:
    r = Report()
    if not isinstance(g, dict):
        r.err("root", "content must be a JSON object")
        return r

    # meta
    m = g.get("meta") or {}
    for f in ("slug", "title", "description", "eyebrow", "researched"):
        if not m.get(f):
            r.err("meta", f"missing '{f}'")
    if m.get("slug") and not ID_RE.match(m["slug"]):
        r.err("meta.slug", "use lowercase letters, digits and hyphens")
    if m.get("title") and not (1 <= len(m["title"].split()) <= 6):
        r.warn("meta.title", "aim for a 2-4 word name")
    if m.get("researched") and not DATE_RE.match(m["researched"]):
        r.err("meta.researched", "use YYYY-MM-DD")

    # entities
    ents = g.get("entities") or []
    ids: set[str] = set()
    hues_used: dict[str, str] = {}
    if not ents:
        r.err("entities", "add at least one entity")
    for i, e in enumerate(ents):
        w = f"entities[{i}]"
        eid = e.get("id", "")
        if not ID_RE.match(eid):
            r.err(w, "id must be lowercase letters, digits and hyphens")
        if eid in ids:
            r.err(w, f"duplicate id '{eid}'")
        ids.add(eid)
        if not e.get("name"):
            r.err(w, "missing 'name'")
        hue = e.get("hue")
        if hue not in HUES:
            r.err(w, f"hue must be one of {sorted(HUES)}")
        elif hue in hues_used:
            r.warn(w, f"hue '{hue}' is already used by '{hues_used[hue]}'; each entity should have its own color")
        else:
            hues_used[hue] = eid
        if "vercel" in eid and hue != "ink":
            r.warn(w, "Vercel entities use the 'ink' hue")
    if len(ents) > 7:
        r.warn("entities", "more than 7 entities makes the color legend hard to learn")

    def ent_ref(where: str, eid, required=False):
        if eid is None:
            if required:
                r.err(where, "missing 'entity'")
            return
        if eid not in ids:
            r.err(where, f"unknown entity '{eid}'")

    def hue_ref(where: str, obj: dict):
        if obj.get("hue") is not None and obj["hue"] not in HUES:
            r.err(where, f"hue must be one of {sorted(HUES)}")
        if obj.get("hue") and obj.get("entity"):
            r.warn(where, "set 'entity' or 'hue', not both")

    # hero
    hero = g.get("hero") or {}
    for f in ("headline", "lede"):
        if not hero.get(f):
            r.err("hero", f"missing '{f}'")
    for c in hero.get("chips") or []:
        ent_ref("hero.chips", c)

    # sections
    secs = g.get("sections") or []
    if not secs:
        r.err("sections", "add at least one section")
    sec_ids: set[str] = set()
    types_seen: list[str] = []
    for i, s in enumerate(secs):
        t = s.get("type")
        w = f"sections[{i}] ({t})"
        if t not in SECTION_FIELDS:
            r.err(w, f"unknown type; use one of {sorted(SECTION_FIELDS)}")
            continue
        types_seen.append(t)
        sid = s.get("id") or f"{t}-{i + 1}"
        if not ID_RE.match(sid):
            r.err(w, "id must be lowercase letters, digits and hyphens")
        if sid in sec_ids or sid == "sources":
            r.err(w, f"duplicate or reserved section id '{sid}'")
        sec_ids.add(sid)
        for f in SECTION_FIELDS[t]:
            if s.get(f) in (None, "", []):
                r.err(w, f"missing '{f}'")

        if t == "layers":
            for j, l in enumerate(s.get("layers") or []):
                lw = f"{w}.layers[{j}]"
                ent_ref(lw, l.get("entity"))
                hue_ref(lw, l)
                for f in ("tag", "name", "analogy"):
                    if not l.get(f):
                        r.err(lw, f"missing '{f}'")
        elif t == "profile":
            ent_ref(w, s.get("entity"), required=True)
            n_why, n_terms = len(s.get("why") or []), len(s.get("terms") or [])
            if n_why and not 3 <= n_why <= 6:
                r.warn(w, f"{n_why} reasons; aim for 3-5")
            if n_terms and not 3 <= n_terms <= 7:
                r.warn(w, f"{n_terms} terms; aim for 4-6")
            for j, term in enumerate(s.get("terms") or []):
                if not (isinstance(term, list) and len(term) == 2):
                    r.err(f"{w}.terms[{j}]", "each term is [term, definition]")
        elif t == "compare":
            cols = s.get("columns") or []
            for c in cols:
                ent_ref(f"{w}.columns", c)
            for j, row in enumerate(s.get("rows") or []):
                if len(row.get("cells") or []) != len(cols):
                    r.err(f"{w}.rows[{j}]", f"has {len(row.get('cells') or [])} cells, expected {len(cols)}")
        elif t == "simulator":
            _validate_simulator(r, w, s, ent_ref, hue_ref)
        elif t == "panels":
            for j, p in enumerate(s.get("panels") or []):
                if p.get("tone", "neutral") not in TONES:
                    r.err(f"{w}.panels[{j}]", f"tone must be one of {sorted(TONES)}")
        elif t == "beforeAfter":
            for side in ("before", "after"):
                f = s.get(side) or {}
                for j, row in enumerate(f.get("rows") or []):
                    rw = f"{w}.{side}.rows[{j}]"
                    if isinstance(row, dict) and "hub" in row:
                        ent_ref(rw, row["hub"].get("entity"))
                        hue_ref(rw, row["hub"])
                    elif isinstance(row, list):
                        for it in row:
                            if isinstance(it, dict) and "text" in it:
                                ent_ref(rw, it.get("entity"))
                                hue_ref(rw, it)
                    else:
                        r.err(rw, "a row is a list of items or a {\"hub\": {...}} object")
            if not s.get("caveat"):
                r.warn(w, "add a 'caveat' saying what Vercel does not cover")
        elif t == "quiz":
            qs = s.get("questions") or []
            for j, q in enumerate(qs):
                qw = f"{w}.questions[{j}]"
                opts = q.get("options") or []
                if len(opts) < 2:
                    r.err(qw, "needs at least 2 options")
                a = q.get("answer")
                if not isinstance(a, int) or not 0 <= a < len(opts):
                    r.err(qw, "answer must be the zero-based index of an option")
                for f in ("prompt", "explain"):
                    if not q.get(f):
                        r.err(qw, f"missing '{f}'")
            answers = [q.get("answer") for q in qs]
            if len(qs) >= 4 and len(set(answers)) == 1:
                r.warn(w, "every correct answer is in the same position; vary it")
        elif t == "prose":
            c = s.get("callout")
            if c and c.get("tone", "neutral") not in TONES:
                r.err(f"{w}.callout", f"tone must be one of {sorted(TONES)}")

    if "quiz" not in types_seen:
        r.warn("sections", "no quiz section; the reader has no way to check what they learned")
    if "layers" not in types_seen:
        r.warn("sections", "no layers section; open with the mental model")

    # sources
    srcs = g.get("sources") or []
    if not srcs:
        r.warn("sources", "no sources listed")
    for i, src in enumerate(srcs):
        if not src.get("title") or not str(src.get("url", "")).startswith("https://"):
            r.err(f"sources[{i}]", "needs a title and an https:// url")

    # inline markup sanity
    for path, text in _text_fields({k: g.get(k) for k in ("hero", "sections")}):
        if text.count("**") % 2:
            r.warn(path, "unbalanced ** bold markers")
        if text.count("`") % 2:
            r.warn(path, "unbalanced ` code markers")
        if re.search(r"<[a-zA-Z/]", text):
            r.warn(path, "HTML tags are shown as plain text; use **bold**, `code` or [label](url)")
    return r


def _validate_simulator(r: Report, w: str, s: dict, ent_ref, hue_ref) -> None:
    dg = s.get("diagram") or {}
    W, H = dg.get("width", 900), dg.get("height", 400)
    names: set[str] = set()
    nodes = {}
    for j, n in enumerate(dg.get("nodes") or []):
        nw = f"{w}.diagram.nodes[{j}]"
        nid = n.get("id", "")
        if not ID_RE.match(nid):
            r.err(nw, "id must be lowercase letters, digits and hyphens")
        if nid in names:
            r.err(nw, f"duplicate id '{nid}'")
        names.add(nid)
        nodes[nid] = n
        for f in ("label", "x", "y", "w", "h"):
            if n.get(f) is None:
                r.err(nw, f"missing '{f}'")
        if all(isinstance(n.get(f), (int, float)) for f in ("x", "y", "w", "h")):
            if n["x"] < 0 or n["y"] < 0 or n["x"] + n["w"] > W or n["y"] + n["h"] > H:
                r.err(nw, f"'{nid}' sits outside the {W}x{H} diagram")
        ent_ref(nw, n.get("entity"))
        hue_ref(nw, n)
    for j, e in enumerate(dg.get("edges") or []):
        ew = f"{w}.diagram.edges[{j}]"
        eid = e.get("id", "")
        if not ID_RE.match(eid):
            r.err(ew, "id must be lowercase letters, digits and hyphens")
        if eid in names:
            r.err(ew, f"id '{eid}' is already used by a node or edge")
        names.add(eid)
        if not e.get("d"):
            for end in ("from", "to"):
                if e.get(end) not in nodes:
                    r.err(ew, f"'{end}' must name a node")
            for side in ("fromSide", "toSide"):
                if e.get(side) and e[side] not in SIDES:
                    r.err(ew, f"{side} must be one of {sorted(SIDES)}")
        ent_ref(ew, e.get("entity"))
        hue_ref(ew, e)
    scs = s.get("scenarios") or []
    if scs and not 2 <= len(scs) <= 6:
        r.warn(w, f"{len(scs)} scenarios; aim for 3-6")
    for j, c in enumerate(scs):
        cw = f"{w}.scenarios[{j}]"
        for f in ("id", "label", "steps", "lesson"):
            if not c.get(f):
                r.err(cw, f"missing '{f}'")
        for key in ("on", "fail"):
            for ref in c.get(key) or []:
                if ref not in names:
                    r.err(cw, f"'{key}' names '{ref}', which is not a node or edge")


def render(g: dict, template: str) -> str:
    m = g["meta"]
    # JSON is embedded in a <script> tag: escape every "<" so content can't close it.
    data = json.dumps(g, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    values = {
        "TITLE": html.escape(m["title"]),
        "DESCRIPTION": html.escape(m.get("description", ""), quote=True),
        "DATA": data,
    }
    return re.sub(r"\{\{(TITLE|DESCRIPTION|DATA)\}\}", lambda mo: values[mo.group(1)], template)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="content JSON files")
    ap.add_argument("--all", action="store_true", help="build every guides/*.json")
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("-o", "--out", default=str(HERE / "dist"), help="output directory (default: dist/)")
    args = ap.parse_args()

    files = [pathlib.Path(f) for f in args.files]
    if args.all:
        files += sorted(GUIDES.glob("*.json"))
    if not files:
        ap.error("give one or more content files, or --all")

    template = TEMPLATE.read_text(encoding="utf-8")
    for ph in ("{{TITLE}}", "{{DATA}}"):
        if ph not in template:
            print(f"template.html is missing the {ph} placeholder", file=sys.stderr)
            return 2

    out_dir = pathlib.Path(args.out)
    failed = False
    for f in files:
        try:
            g = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"✗ {f}: can't read JSON ({exc})")
            failed = True
            continue
        rep = validate(g)
        for wmsg in rep.warnings:
            print(f"  warning  {wmsg}")
        for emsg in rep.errors:
            print(f"  error    {emsg}")
        if rep.errors:
            print(f"✗ {f}: {len(rep.errors)} error(s), not built")
            failed = True
            continue
        if args.check:
            print(f"✓ {f}: valid ({len(rep.warnings)} warning(s))")
            continue
        page = render(g, template)
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / f"{g['meta']['slug']}.html"
        dest.write_text(page, encoding="utf-8")
        size = dest.stat().st_size
        note = "  (over 1 MB; trim content)" if size > 1_000_000 else ""
        print(f"✓ {f} → {dest} ({size / 1024:.0f} KB, {len(rep.warnings)} warning(s)){note}")
        if g["meta"].get("published_url"):
            print(f"  republish to {g['meta']['published_url']} to update the live page")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
