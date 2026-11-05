#!/usr/bin/env python3
"""Inventory, overlap and check helpers for skill-merger. Standard library only.

  skills.py inventory [--json] [--root DIR ...]
  skills.py overlap   [--min 0.12] [--root DIR ...]
  skills.py check     SKILL_DIR
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STOP = set("""a an and are as at be by can do for from has have how i in into is it its of on or
that the their them this to use used uses using when where which while who with without you your
skill skills user users asks ask wants want need needs any all also e g eg etc such like via
one more most other not no than then these those what about over""".split())


def parse_frontmatter(text):
    """Minimal YAML frontmatter reader: top-level scalars and | / > blocks."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    lines = text[3:end].strip("\n").splitlines()
    data, i = {}, 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        i += 1
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "" or val[0] in "|>":
            block = []
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            if val == "" and block and re.match(r"^[A-Za-z0-9_-]+:(\s|$)", block[0]):
                val = {}  # nested map such as metadata:, not needed here
            elif val == "":  # plain scalar continued on the next lines
                val = " ".join(block).strip()
            else:
                val = ("\n" if val[0] == "|" else " ").join(block).strip()
        elif len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        data[key] = val
    return data


def read_skill(skill_md, source):
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text) or {}
    folder = skill_md.parent
    words = sum(len(p.read_text(encoding="utf-8", errors="replace").split())
                for p in folder.rglob("*.md")
                if ".git" not in p.parts and p.name not in ("MERGE-LEDGER.md", "SOURCES.md"))
    desc = fm.get("description", "")
    return {
        "name": fm.get("name") or folder.name,
        "folder": folder.name,
        "source": source,
        "path": str(folder),
        "words": words,
        "user_invoked": str(fm.get("disable-model-invocation", "")).lower() == "true",
        "description": " ".join(desc.split()) if isinstance(desc, str) else "",
    }


def skill_files(root, max_depth):
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
        if depth >= max_depth:
            dirnames[:] = []
        if "SKILL.md" in filenames:
            yield Path(dirpath) / "SKILL.md"
            dirnames[:] = []  # a skill folder does not contain other skills


def plugin_roots():
    f = HOME / ".claude" / "plugins" / "installed_plugins.json"
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    roots = []
    for plugin, installs in (data.get("plugins") or {}).items():
        for inst in installs:
            if inst.get("installPath"):
                roots.append((Path(inst["installPath"]), "plugin:" + plugin))
    return roots


def inventory(extra_roots):
    roots = [
        (HOME / ".claude" / "skills", "user"),
        (HOME / ".agents" / "skills", "agents"),
        (Path.cwd() / ".claude" / "skills", "project"),
    ] + [(Path(r).expanduser(), "extra") for r in extra_roots]
    seen, skills = set(), []
    for root, source in roots:
        for md in skill_files(root, 2):
            real = os.path.realpath(md.parent)
            if real not in seen:
                seen.add(real)
                skills.append(read_skill(md, source))
    for root, source in plugin_roots():
        for md in skill_files(root, 4):
            real = os.path.realpath(md.parent)
            if real not in seen:
                seen.add(real)
                skills.append(read_skill(md, source))
    return sorted(skills, key=lambda s: (s["source"], s["name"]))


def tokens(text):
    words = re.findall(r"[a-z0-9][a-z0-9+#.-]*[a-z0-9+#]|[a-z0-9]", text.lower())
    return {w for w in words if w not in STOP and len(w) > 2}


def overlap(skills, min_score):
    toks = [tokens(s["name"].replace("-", " ") + " " + s["description"]) for s in skills]
    parent = list(range(len(skills)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = []
    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            if not toks[i] or not toks[j]:
                continue
            shared = toks[i] & toks[j]
            score = len(shared) / len(toks[i] | toks[j])
            if score >= min_score:
                pairs.append((score, i, j, shared))
                parent[find(i)] = find(j)
    groups = {}
    for i in range(len(skills)):
        groups.setdefault(find(i), []).append(i)
    clusters = [g for g in groups.values() if len(g) > 1]
    return clusters, pairs


def check(skill_dir):
    d = Path(skill_dir).expanduser().resolve()
    errors, warns = [], []
    md = d / "SKILL.md"
    if not md.is_file():
        return [f"no SKILL.md in {d}"], []
    text = md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append("SKILL.md has no --- frontmatter block at the top")
        fm = {}
    name = fm.get("name", "")
    if not name:
        errors.append("frontmatter: missing name")
    elif not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"frontmatter: name '{name}' must be lowercase letters, digits, hyphens, <= 64 chars")
    elif name != d.name:
        errors.append(f"frontmatter: name '{name}' differs from folder name '{d.name}'")
    desc = fm.get("description", "")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("frontmatter: missing description")
    else:
        if len(desc) > 1024:
            errors.append(f"frontmatter: description is {len(desc)} chars, limit is 1024")
        if "<" in desc or ">" in desc:
            errors.append("frontmatter: description must not contain < or >")
    n_lines = text.count("\n")
    if n_lines > 500:
        warns.append(f"SKILL.md is {n_lines} lines; move branch-only material to references/")

    for f in sorted(d.rglob("*.md")):
        if ".git" in f.parts:
            continue
        rel = f.relative_to(d)
        body = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\]\(([^)\s]+)\)", body):
            if re.match(r"^([a-z]+:|#|mailto:)", target):
                continue
            path = target.split("#")[0]
            if path and not (f.parent / path).exists():
                errors.append(f"{rel}: broken link -> {target}")
        for path in re.findall(r"`((?:scripts|references|assets)/[^`\s<>*]+)`", body):
            if not (d / path).exists():
                warns.append(f"{rel}: mentions `{path}`, which does not exist (fine if it is an example)")
    return errors, warns


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="skill-merger helpers")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inventory", help="list installed skills")
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", action="append", default=[], help="extra skill folder to scan")
    p = sub.add_parser("overlap", help="suggest clusters of similar skills")
    p.add_argument("--min", type=float, default=0.12, help="minimum Jaccard score (0-1)")
    p.add_argument("--root", action="append", default=[])
    p = sub.add_parser("check", help="validate a skill folder")
    p.add_argument("dir")
    a = ap.parse_args()

    if a.cmd == "inventory":
        skills = inventory(a.root)
        if a.json:
            print(json.dumps(skills, indent=2, ensure_ascii=False))
            return 0
        for s in skills:
            flag = " [user-invoked]" if s["user_invoked"] else ""
            folder = "" if s["folder"] == s["name"] else f" [folder: {s['folder']}]"
            print(f"{s['name']}{folder}  ({s['source']}, {s['words']} words){flag}\n  {s['path']}\n  {s['description'][:200]}\n")
        print(f"{len(skills)} skills")
        return 0

    if a.cmd == "overlap":
        skills = inventory(a.root)
        clusters, pairs = overlap(skills, a.min)
        if not clusters:
            print(f"No pairs above {a.min}. Try --min 0.1, then judge descriptions yourself.")
            return 0
        for n, c in enumerate(sorted(clusters, key=len, reverse=True), 1):
            print(f"Cluster {n}: " + ", ".join(skills[i]["name"] for i in c))
            for score, i, j, shared in sorted(pairs, reverse=True, key=lambda p: p[0]):
                if i in c:
                    print(f"  {score:.2f}  {skills[i]['name']} ~ {skills[j]['name']}: {' '.join(sorted(shared)[:8])}")
            print()
        print("Word overlap is a hint. Confirm each cluster by reading the descriptions.")
        return 0

    errors, warns = check(a.dir)
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    if errors:
        return 1
    print("OK" + (f" ({len(warns)} warnings)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
