# Contributing

Thanks for helping out. Bug reports, merge stories and pull requests are all welcome.

## Reporting a problem

If a merge lost something, kept something it shouldn't have, or the merged skill stopped firing, open an issue with the "Merge problem" template. The ledger (`MERGE-LEDGER.md` in the archive folder) is the most useful thing you can attach, because it shows what the agent decided for each unit.

For bugs in `scripts/skills.py`, use the "Bug report" template and include the command you ran and its output.

## Working on it

There are no dependencies. You need Python 3.8 or newer.

```bash
python3 -m unittest discover -s tests   # unit tests for the helper script
python3 scripts/skills.py check .       # the skill checks itself
```

CI runs both, plus `claude plugin validate --strict .` and a skills CLI install dry run. If you have Claude Code installed, run the plugin check locally too.

A few house rules:

- `scripts/skills.py` stays standard library only, so it runs anywhere a skill does.
- `SKILL.md` is read by an agent on every merge. Keep it short and keep each step ending on a "Done when" line. Longer material belongs in `references/`.
- If you change the frontmatter parser, add a test with the frontmatter that broke it.

## Releasing

Bump the version in three places together: `metadata.version` in `SKILL.md`, `version` in `.claude-plugin/plugin.json`, and a new entry at the top of `CHANGELOG.md`. Then tag the commit `vX.Y.Z`.
