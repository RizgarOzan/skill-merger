# Skill Merger

[![Validate](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml/badge.svg)](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![skills.sh](https://skills.sh/b/RizgarOzan/skill-merger)](https://skills.sh/RizgarOzan/skill-merger)

**English** · [Türkçe](README.tr.md)

Install skills for a few months and you end up with three Unity UI skills, two commit skills and four design-review skills that half overlap. The agent loads the wrong one, or two that disagree, and every one of those descriptions sits in context on every turn.

Skill Merger folds a group like that into one skill. Nothing disappears quietly: every rule, step and script from every source gets a row in a ledger saying where it went, or why it was dropped. When two sources disagree, you decide. The old skills go to an archive folder, not the trash.

It's plain Markdown plus one Python script with no dependencies, so it works with any agent that reads skills: Claude Code, Claude Desktop, Codex, Cursor, OpenCode.

## Contents

- [Install](#install)
- [Use](#use)
- [What it does](#what-it-does)
- [The ledger](#the-ledger)
- [The helper script](#the-helper-script)
- [Safety](#safety)
- [FAQ](#faq)
- [Contributing](#contributing)

## Install

With the [skills CLI](https://skills.sh):

```bash
npx skills add RizgarOzan/skill-merger --global
```

As a Claude Code plugin:

```text
/plugin marketplace add RizgarOzan/skill-merger
/plugin install skill-merger@skill-merger
```

By hand: copy this folder to `~/.claude/skills/skill-merger/`, or to your agent's skill folder.

## Use

Just ask:

```text
I have too many UI skills, merge the ones that overlap
```

```text
Merge unity-ui, unity-ui-toolkit and ui-uitk into one skill called unity-ui
```

```text
Which of my skills overlap?
```

Or call it directly with `/skill-merger` (`/skill-merger:skill-merger` when installed as a plugin).

## What it does

| Step | What happens | Who decides |
|---|---|---|
| 1. Inventory | Lists every skill you have: your own, project skills, plugin skills | |
| 2. Clusters | Suggests groups that overlap and a name for each merged skill | **you** confirm |
| 3. Read | Reads every file of every source, not just `SKILL.md` | |
| 4. Ledger | Splits each source into units and gives each one a verdict | **you** settle conflicts |
| 5. Write | Shared rules go in `SKILL.md`, the rest in `references/`, scripts in `scripts/` | |
| 6. Verify | Runs the checker, walks the ledger, checks the old triggers still fire | |
| 7. Retire | Moves the old skills to `~/.claude/skills-archive/` | **you** approve |

The merged skill ends up shaped like this:

```
unity-ui/
├── SKILL.md              shared rules and a "which file to read" table
├── references/
│   ├── choosing-a-ui-system.md
│   ├── ugui.md
│   └── ui-toolkit.md
├── scripts/
└── SOURCES.md            who wrote what, under which license
```

## The ledger

The ledger is what keeps a merge honest. These rows come from a test run that merged three Unity UI skills. The last one shows the `update` verdict, which I added after that run turned up content that was dated but still needed:

| Source | Unit | Verdict | Goes to |
|---|---|---|---|
| unity-ui | Quick Start UGUI button | keep | `SKILL.md` § Quick start |
| unity-ui | UI Systems Comparison table | merge with two other tables | `choosing-a-ui-system.md` |
| unity-ui | Best Practices 4–7 | keep, they apply to both systems | `SKILL.md` § Rules |
| unity-ui | `requires: unity-csharp-fundamentals` | drop: that skill isn't installed | — |
| unity-ui-toolkit | `UxmlFactory` custom control | update: pre-Unity 6 API, kept with a version note | `ui-toolkit.md` |

Each unit gets one of five verdicts: **keep**, **merge**, **update** (still needed but dated), **conflict** (goes to you), or **drop** (with a reason). The merge isn't done until every row has one. Afterwards the ledger moves to the archive next to the old skills, so you can always see what happened.

## The helper script

`scripts/skills.py` also works on its own:

```bash
python3 scripts/skills.py inventory            # every installed skill, with word counts
python3 scripts/skills.py overlap              # groups that look alike
python3 scripts/skills.py check path/to/skill  # frontmatter, name, description length, broken links
```

On my machine, with 88 skills installed, `overlap` found this group among others:

```text
Cluster 4: linkedin-analyze, linkedin-network, linkedin-post, linkedin-profile
  0.15  linkedin-analyze ~ linkedin-post: linkedin log own post reach week
  0.14  linkedin-post ~ linkedin-profile: against linkedin reach rewrite why
```

It only compares the words in descriptions, so take it as a first guess. The agent reads the descriptions itself before it proposes anything.

## Safety

- It never deletes anything. Old skills are moved to `~/.claude/skills-archive/<date>-<name>/`, and moving them back undoes the merge.
- It doesn't touch the source folders until the new skill has passed its checks and you've said yes.
- Plugin skills are never edited, because the next plugin update would overwrite them. Their content is copied into the new skill, and you decide whether to disable the plugin.
- Skills installed with the skills CLI are removed with `npx skills remove`, so no broken links or lock file entries are left behind.
- When a source has no license, or another author's license, the merged skill records it in `SOURCES.md` and is marked private-only where needed.

## FAQ

**Does it work with skills I didn't write?**
Yes. Third-party skills are the usual case. Their authors and licenses are listed in `SOURCES.md`. MIT and Apache content can be merged and shared. Unlicensed content is fine for your own use but shouldn't be published.

**What if two skills give opposite advice?**
That's a conflict. All conflicts come to you in one question. If nobody's around to answer, the agent picks, marks the row `settled by agent`, and lists those picks first in its report.

**Will the merged skill still fire when the old ones did?**
That's step 6. For each old skill, the agent writes the request that used to trigger it and checks that the new description covers it. If it can start a subagent, it gets a second opinion so it isn't grading its own work.

**Can I merge just two skills?**
Sure. A cluster is any two or more.

## Contributing

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE) © 2026 Rızgar Ozan
