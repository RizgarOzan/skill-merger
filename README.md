# Skill Merger

[![Validate](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml/badge.svg)](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml)

Install skills for a while and you end up with three Unity UI skills, two commit skills and four design-review skills that half overlap. The agent picks the wrong one, or loads two that disagree, and every description eats context on every turn.

Skill Merger folds a group of skills that cover the same thing into one. Nothing gets lost quietly: every rule, step and script from every source gets a row in a ledger that says where it went or why it was dropped. When two sources disagree, you decide. The old skills go to an archive folder, not the trash.

It's plain Markdown plus one Python script with no dependencies, so it works with any agent that supports skills: Claude Code, Claude Desktop, Codex, Cursor, OpenCode.

*Türkçe: Aynı konuda birden fazla skill'in varsa (üç Unity UI skill'i, iki commit skill'i...) bunları tek bir skill'de birleştirir. Her kaynaktaki her kural ve script için nereye gittiğini ya da neden atıldığını yazan bir kayıt tutar, çelişkilerde sana sorar, eski skilleri silmez, arşive taşır.*

## Install

With the skills CLI:

```bash
npx skills add RizgarOzan/skill-merger --global
```

As a Claude Code plugin:

```text
/plugin marketplace add RizgarOzan/skill-merger
/plugin install skill-merger@skill-merger
```

By hand: copy this folder to `~/.claude/skills/skill-merger/` (or your agent's skill folder).

## Use

Ask in plain words:

```text
I have too many UI skills, merge the ones that overlap
```

```text
Merge unity-ui, unity-ui-toolkit and ui-uitk into one skill called unity-ui
```

```text
/skill-merger
```

What happens:

1. Inventory. Lists every skill you have: your own, project skills, and plugin skills.
2. Clusters. Suggests groups that overlap. You confirm which ones to merge and what to call the result.
3. Read. Reads every file of every source, not just `SKILL.md`.
4. Ledger. Splits each source into rules, steps, references and scripts, and marks each one keep, merge, conflict or drop. All conflicts come to you in one question.
5. Write. Builds the new skill: shared rules in `SKILL.md`, the parts only some requests need in `references/`, scripts in `scripts/`.
6. Verify. Runs the checker, walks the ledger, and checks that whatever used to trigger each old skill still triggers the new one.
7. Retire. With your OK, moves the old skills to `~/.claude/skills-archive/<date>/`. Moving them back undoes the merge.

Plugin skills can't be edited in place because updates overwrite them. Their content gets copied into the new skill, and you decide whether to disable the plugin.

## The helper script

`scripts/skills.py` also works on its own:

```bash
python3 scripts/skills.py inventory          # every installed skill, with word counts
python3 scripts/skills.py overlap            # groups that look alike
python3 scripts/skills.py check path/to/skill  # frontmatter, name, description length, broken links
```

`overlap` only compares words in descriptions. It's a starting point, and the agent reads the descriptions before proposing anything to you.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/skills.py check .
```

CI runs both, plus `claude plugin validate --strict .` and a skills CLI discovery check.

## License

MIT
