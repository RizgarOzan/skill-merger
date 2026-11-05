---
name: skill-merger
description: |
  Merge overlapping agent skills from the same category into one skill without losing what any of them did.
  Use when the user has several skills covering one topic (three Unity skills, two commit skills, a pile of
  design-review skills), asks to merge, consolidate, combine or deduplicate skills, says their skill list is
  cluttered or the wrong skill keeps firing, or wants to audit installed skills for overlap.
license: MIT
metadata:
  version: 1.0.0
---

# Skill Merger

Turns a **cluster** of skills that cover one category into a single skill. The merged skill keeps every live rule, step and script from its sources; what it drops, it drops on purpose with a recorded reason. The originals are archived, never deleted.

The leading word is **ledger**: every unit of content from every source gets a row saying where it went. The merge is done when the ledger has no empty rows.

`scripts/skills.py` (Python 3.8+, standard library only) does the mechanical parts. Run it with `python3` (or `python` on Windows):

| Command | What it does |
|---|---|
| `skills.py inventory [--json]` | Lists every installed skill: name, source, path, word count, description |
| `skills.py overlap [--min 0.12]` | Suggests clusters from description word overlap |
| `skills.py check <dir>` | Validates a skill folder: frontmatter, name, description length, every relative link and script path |

## 1. Inventory

Run `skills.py inventory`. It reads `~/.claude/skills` (source `user`), `~/.agents/skills` (source `agents`), project skills in `./.claude/skills` (`project`) and installed plugin skills (`plugin:<name>`, from `~/.claude/plugins/installed_plugins.json`). Pass `--root <dir>` to add another location, such as another agent's skill folder.

Source `agents` means the skill lives in the skills CLI folder with no link in `~/.claude/skills`, so Claude Code does not load it (other agents may). Tell the user when a cluster member has this source.

If the user already named the skills to merge, find them in the list (by name or by the `[folder: …]` tag) and skip to step 3. A skill the user named that the inventory does not show is a stop: ask where it lives.

Done when: every skill the user mentioned is located on disk.

## 2. Find clusters

Run `skills.py overlap` for candidates, then read the descriptions yourself. Word overlap is a hint; a cluster is skills a user would reach for **in the same situation**. `unity-testing` and `unity-save-system` share words but answer different questions; `commit-helper` and `conventional-commits` share few words and answer the same one.

Union-find chaining can join unrelated skills into one big candidate, or split a real cluster in two; regroup by hand.

Show the user each proposed cluster: member names, one line on what each covers, and a proposed name for the merged skill. Let them confirm, drop members, or rename. If a plugin skill overlaps the cluster, offer it as a member: a plugin skill left out keeps competing with the merged one. Merge only clusters the user confirmed.

Done when: the user has confirmed at least one cluster and its target name.

## 3. Read every source in full

For each skill in the cluster, read `SKILL.md` and every file in its folder: references, scripts, assets, evals. A merge built from skimmed sources silently loses the one rule that mattered.

Note for each source: its license, its author, and whether it comes from a plugin (`source: plugin` in the inventory). Plugin files get overwritten on update, so a plugin skill is merged by copying its content into the new skill and disabling the plugin afterwards, never by editing it in place.

Done when: you have opened every file in every source folder.

## 4. Build the ledger

Break each source into **units**: one rule, one step, one reference section, one script, one example set. Write the ledger to `MERGE-LEDGER.md` inside the new skill's folder, one row per unit:

| Source | Unit | Verdict | Goes to |
|---|---|---|---|
| `commit-helper` | "subject ≤ 50 chars" | merge with conventional-commits #3 | `SKILL.md` § Message format |
| `commit-helper` | `scripts/lint.sh` | keep | `scripts/lint-commit.sh` |
| `git-tips` | intro paragraph | drop: restates the description | — |

Verdicts:

- **keep**: unique to one source, moves over as is.
- **update**: still needed but dated (an old API, an old version number). Carry it over with the version it applies to, or rewrite it if you know the current form; never drop it as stale just because it is old.
- **merge**: two or more sources say the same thing; write it once, in the clearest wording.
- **conflict**: sources disagree (one says 50-char subjects, the other 72). Collect all conflicts and ask the user to settle them in one question. When nobody can answer (an unattended run), pick, write `settled by agent: <why>` in the row, and list those picks first in the report.
- **drop**: wrong, a no-op the model follows anyway, pure restatement, or a pointer to a skill, agent or file that does not exist. The reason goes in the row.

A unit that belongs in two places gets one row with both locations in "Goes to".

Licenses are units too. When any source was written by someone other than the user, the merged skill lists every source with its author and license in a `SOURCES.md`. A source with no license, or one that forbids modification, is fine for private use but not for publishing: tell the user before merging it, and mark the merged skill private in `SOURCES.md`.

Done when: every unit from step 3 has a row with a verdict, and every conflict is settled by the user (or, unattended, marked `settled by agent`).

## 5. Write the merged skill

Read [references/structure.md](references/structure.md) before writing. It covers the router layout, writing the description, and moving scripts.

In short: shared rules and the common workflow go in `SKILL.md`; material only some situations need goes in `references/<topic>.md` behind a one-line pointer; scripts move to `scripts/` with every path in the text updated.

Write the new skill into a fresh folder in the skills folder the user's agent loads: `~/.claude/skills/<new-name>/` for Claude Code, even when the sources sat in `~/.agents/skills`; `./.claude/skills/<new-name>/` if every source was a project skill. Do not touch the source folders yet.

Done when: every ledger row marked keep, merge or settled conflict appears at its "Goes to" location.

## 6. Verify

1. Run `skills.py check <new-skill-dir>`. Fix every `ERROR` and run it again until it prints `OK`. Open each `WARN`: a missing path in an example is fine, a missing path the agent will follow is not.
2. Walk the ledger top to bottom and open each "Goes to" location. Each row is either present there or marked drop with a reason.
3. Trigger check: for each source skill, write the request that used to fire it. Read the merged description and confirm the request matches one of its trigger branches. A source whose trigger the description no longer carries is a lost skill; add the branch. You wrote the description, so you will tend to pass it: when you can start a subagent, give it only the merged description and the old requests and ask which ones would fire it.

Report to the user: the new skill's path, its word count against the sources' combined word count (`inventory` leaves `MERGE-LEDGER.md` and `SOURCES.md` out of both), the dropped units with reasons, and the trigger check result.

Done when: `check` prints `OK`, every ledger row is confirmed, and every source's trigger request maps to the merged description.

## 7. Retire the originals

Ask before this step; it changes what the user's agent can see.

The archive for one merge is one folder: `~/.claude/skills-archive/<YYYY-MM-DD>-<new-name>/`, holding each source folder under its own name plus the ledger.

- **User and project skills**: move each source folder into the archive. Moving, not deleting, keeps the way back one command long. Skills outside the skills folder are not loaded, so the archive does not compete with the new skill.
- **Plugin skills**: you cannot remove one skill from a plugin. Tell the user to run `/plugin` and disable the plugin, or keep it if the plugin brings other skills they use; in that case the overlap remains and the user should know it.
- **Skills CLI skills** (source `agents`, or a `~/.claude/skills/<name>` link pointing into `~/.agents/skills`, or a name listed in `~/.agents/.skill-lock.json`): copy the real folder into the archive, then run `npx skills remove <name> --global` so the link and the lock entry go with it. Removing only the folder leaves a dangling link and a lock entry that reinstalls it.

Move `MERGE-LEDGER.md` from the new skill into the archive folder, so the record of the merge sits beside the originals and does not ship with the skill.

Tell the user to restart the agent or reload skills so the change takes effect, and how to undo: move the folder back from the archive.

Done when: no source skill is still in a loaded skill folder (except plugin skills the user chose to keep), and the user knows the archive path.
