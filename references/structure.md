# Structure of a merged skill

How to lay out the skill that replaces a cluster. Read this in step 5 of `SKILL.md`.

## Layout

```
<new-name>/
├── SKILL.md            shared rules, common workflow, a branch table
├── references/
│   └── <topic>.md      one file per branch only some requests need
├── scripts/            every script from every source, renamed if names clash
├── SOURCES.md          when any source was written by someone other than the user
└── MERGE-LEDGER.md     the ledger; moves to the archive in step 7
```

## What goes where

The test for each unit is **branching**: does every request this skill handles need it?

- **Yes** → `SKILL.md`. Shared rules, the common workflow, safety rules, anything a wrong guess would make costly.
- **Only some requests** → `references/<topic>.md`, reached from a branch table in `SKILL.md`:

  ```markdown
  | When the request is about | Read |
  |---|---|
  | Tilemaps, RuleTiles, palettes | [references/tilemap.md](references/tilemap.md) |
  | Sprite slicing, atlases | [references/sprites.md](references/sprites.md) |
  ```

  Name topics after the situation, not after the old skill. `tilemap.md` stays meaningful a year later; `unity-tilemap-helper-v2.md` does not.

A source that covers several topics gets split across branches by topic; one source does not have to map to one file. A source that was already well split (its own `SKILL.md` plus references) and covers one topic usually becomes one branch: its `SKILL.md` body turns into `references/<topic>.md`, its references move beside it, and links get rewritten.

Keep `SKILL.md` under about 500 lines. If the shared core alone is longer than that, the cluster may really be two clusters; say so to the user rather than forcing one skill.

## Writing the description

The description is the only part always in the agent's context, and it alone decides when the merged skill fires. Build it from the sources' descriptions:

1. List every distinct **trigger branch** across all sources: a situation, a request phrasing, a file type, a tool name the user types.
2. Collapse synonyms. "merge", "combine" and "consolidate" for one situation are one branch; keep the two words the user most likely types.
3. First sentence: what the skill does, in plain words. Then "Use when …" with the branches.
4. Stay under 1024 characters (`skills.py check` enforces it). If the branches do not fit, the cluster is too wide.

Keep the user's own vocabulary. If they called it "the commit skill", the word "commit" must be in the description.

## Scripts and assets

- Copy scripts into `scripts/`. If two sources have `scripts/run.py`, rename both after what they do (`scripts/lint-commit.py`, `scripts/changelog.py`).
- Update every mention of a moved file in the text. `skills.py check` reports links and `scripts/…` paths that do not resolve.
- Scripts that read paths relative to their own skill folder (`Path(__file__).parent / "data.json"`) need their data moved alongside, keeping the same relative layout.
- If two scripts do the same job, keep the better one and record the other as a drop in the ledger, with the reason.

## Frontmatter

- `name`: lowercase letters, digits and hyphens, at most 64 characters, equal to the folder name.
- `description`: as above.
- Keep any other field a source used that still applies (`license`, `allowed-tools`, `disable-model-invocation`, `metadata`). If sources disagree on `allowed-tools`, use the union of their lists; if any source has no `allowed-tools` at all, leave the field out (no restriction). Tell the user either way. If one source set `disable-model-invocation: true` and another did not, that is a conflict for the user: a user-invoked merge loses automatic triggering.

## SOURCES.md

When any source was written by someone other than the user (unknown author counts):

```markdown
# Sources

This skill merges:

| Skill | Author | License | Upstream |
|---|---|---|---|
| commit-helper | Jane Doe | MIT | https://github.com/jane/commit-helper |
| conventional-commits | — | Apache-2.0 | https://github.com/x/y |
```

MIT and Apache-2.0 content can be merged; keep both license texts if the user publishes the result. Unlicensed content is "all rights reserved" by default: fine for the user's private use, not for publishing.
