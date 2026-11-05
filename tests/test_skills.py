import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import skills  # noqa: E402


def make_skill(root, name, text, files=None):
    d = Path(root) / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(text, encoding="utf-8")
    for rel, body in (files or {}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return d


class Frontmatter(unittest.TestCase):
    def test_inline(self):
        fm = skills.parse_frontmatter('---\nname: a\ndescription: "Does a."\n---\nbody')
        self.assertEqual(fm, {"name": "a", "description": "Does a."})

    def test_literal_block(self):
        fm = skills.parse_frontmatter("---\nname: a\ndescription: |\n  line one\n  line two\nlicense: MIT\n---\n")
        self.assertEqual(fm["description"], "line one\nline two")
        self.assertEqual(fm["license"], "MIT")

    def test_plain_scalar_on_next_lines(self):
        fm = skills.parse_frontmatter("---\nname: a\ndescription:\n  wraps onto\n  two lines\n---\n")
        self.assertEqual(fm["description"], "wraps onto two lines")

    def test_nested_map_is_skipped(self):
        fm = skills.parse_frontmatter("---\nname: a\nmetadata:\n  version: 1.0.0\ndescription: d\n---\n")
        self.assertEqual(fm["metadata"], {})
        self.assertEqual(fm["description"], "d")

    def test_missing(self):
        self.assertIsNone(skills.parse_frontmatter("# no frontmatter"))


class Check(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_skill(t, "good", "---\nname: good\ndescription: Does good things.\n---\nSee [ref](references/r.md).\n",
                           {"references/r.md": "ok"})
            self.assertEqual(skills.check(d), ([], []))

    def test_broken_link_and_bad_name(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_skill(t, "bad", "---\nname: Bad Name\ndescription: x\n---\n[gone](references/gone.md)\n")
            errors, _ = skills.check(d)
            self.assertTrue(any("name" in e for e in errors))
            self.assertTrue(any("broken link" in e for e in errors))

    def test_long_description(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_skill(t, "long", "---\nname: long\ndescription: " + "x" * 1100 + "\n---\n")
            errors, _ = skills.check(d)
            self.assertTrue(any("1024" in e for e in errors))

    def test_links_in_code_blocks_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            d = make_skill(t, "code", "---\nname: code\ndescription: d\n---\n```\n[x](nope.md)\n```\n")
            self.assertEqual(skills.check(d)[0], [])


class Overlap(unittest.TestCase):
    def test_similar_skills_cluster(self):
        s = [
            {"name": "commit-helper", "description": "Write git commit messages in conventional commit format."},
            {"name": "conventional-commits", "description": "Conventional commit messages for git commits."},
            {"name": "pdf", "description": "Read and fill PDF forms."},
        ]
        clusters, _ = skills.overlap(s, 0.12)
        self.assertEqual([sorted(c) for c in clusters], [[0, 1]])


if __name__ == "__main__":
    unittest.main()
