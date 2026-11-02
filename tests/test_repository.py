"""Ensure the public artifact remains compact, navigable and predictable."""
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import flow_parity as fp  # noqa: E402


class RepositoryTests(unittest.TestCase):
    def test_skill_frontmatter(self):
        text = (ROOT / ".agents/skills/flow-parity/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        head = text.split("---\n", 2)[1]
        self.assertRegex(head, r"(?m)^name: flow-parity$")
        self.assertRegex(head, r"(?m)^description: .{50,}$")
        self.assertTrue((ROOT / ".agents/skills/flow-parity/agents/openai.yaml").is_file())

    def test_references_exist(self):
        text = (ROOT / ".agents/skills/flow-parity/SKILL.md").read_text(encoding="utf-8")
        folder = ROOT / ".agents/skills/flow-parity"
        for dest in re.findall(r"\]\((references/[^)#]+)\)", text):
            self.assertTrue((folder / dest).is_file(), dest)

    def test_required_bilingual_docs(self):
        for name in ["README", "CHANGELOG", "CONTRIBUTING", "SECURITY"]:
            self.assertTrue((ROOT / f"{name}.md").is_file())
            self.assertTrue((ROOT / f"{name}.ru.md").is_file())
        for name in ["architecture", "usage", "security", "development"]:
            self.assertTrue((ROOT / "docs/en" / f"{name}.md").is_file())
            self.assertTrue((ROOT / "docs/ru" / f"{name}.md").is_file())

    def test_relative_markdown_links(self):
        for source in ROOT.rglob("*.md"):
            if ".git" in source.parts:
                continue
            text = source.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                relative = target.split("#", 1)[0]
                self.assertTrue((source.parent / relative).is_file(), f"{source.relative_to(ROOT)}: {relative}")

    def test_manifest_test_unhashable_flow_id(self):
        doc = fp.load(ROOT / "examples/demo.json")
        doc["tests"][0]["flow_id"] = {"invalid": "object"}
        self.assertTrue(any("unknown flow_id" in e for e in fp.validate(doc)))

    def test_synthetic_example_disclosed(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("synthetic test data", text)
        self.assertIn("not", text.lower())


if __name__ == "__main__":
    unittest.main()
