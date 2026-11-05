# Changelog

## 1.0.0 (2026-11-06)

First release.

- Seven-step merge workflow: inventory, clusters, full read, ledger, write, verify, retire.
- Ledger verdicts: keep, update, merge, conflict, drop.
- `scripts/skills.py` with `inventory`, `overlap` and `check`.
- Finds skills in `~/.claude/skills`, `~/.agents/skills`, project `.claude/skills` and installed Claude Code plugins.
- Retires skills CLI installs with `npx skills remove` so no dangling links are left.
- Installs as a Claude Code plugin or with `npx skills add`.
