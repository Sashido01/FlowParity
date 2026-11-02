"""Pure offline checks. The demo is synthetic, not a release approval."""
import copy
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import flow_parity as fp  # noqa: E402


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = fp.load(ROOT / "examples" / "demo.json")

    def edit(self):
        return copy.deepcopy(self.doc)

    def test_demo_valid(self):
        self.assertEqual(fp.validate(self.doc), [])

    def test_demo_recorded_gate(self):
        result = fp.evaluate(self.doc)
        self.assertTrue(result["recorded_gate_pass"])
        self.assertEqual(result["coverage"]["must"]["verified"], 1)
        self.assertEqual(result["coverage"]["should"]["verified"], 0)

    def test_missing_must_blocks(self):
        d = self.edit()
        d["features"][0]["status"] = "partial"
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_failed_test_blocks(self):
        d = self.edit()
        d["tests"][0]["status"] = "failed"
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_no_review_blocks(self):
        d = self.edit()
        d["review"]["approved_for_release"] = False
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_no_security_review_blocks(self):
        d = self.edit()
        d["review"]["security_review"] = "not_run"
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_no_must_blocks(self):
        d = self.edit()
        d["features"][0]["priority"] = "should"
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_no_flow_blocks(self):
        d = self.edit()
        d["flows"] = []
        d["tests"] = []
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_unmapped_must_blocks(self):
        d = self.edit()
        d["flows"][0]["feature_ids"] = ["FEAT-002"]
        self.assertFalse(fp.evaluate(d)["recorded_gate_pass"])

    def test_no_features_invalid(self):
        d = self.edit()
        d["features"] = []
        self.assertIn("at least one", " ".join(fp.validate(d)))

    def test_duplicate_id_invalid(self):
        d = self.edit()
        d["features"].append(copy.deepcopy(d["features"][0]))
        self.assertIn("duplicate id", " ".join(fp.validate(d)))

    def test_unknown_reference_invalid(self):
        d = self.edit()
        d["features"][0]["source_ids"] = ["SRC-999"]
        self.assertIn("unknown reference", " ".join(fp.validate(d)))

    def test_verified_requires_proof(self):
        d = self.edit()
        d["features"][0]["evidence_ids"] = []
        self.assertIn("nonempty list", " ".join(fp.validate(d)))

    def test_passed_test_requires_proof(self):
        d = self.edit()
        d["tests"][0]["evidence_ids"] = []
        self.assertIn("nonempty list", " ".join(fp.validate(d)))

    def test_bad_authorization_invalid(self):
        d = self.edit()
        d["sources"][0]["kind"] = "authorized"
        self.assertIn("permission_note", " ".join(fp.validate(d)))

    def test_public_basis_cannot_use_owned(self):
        d = self.edit()
        d["reference"]["basis"] = "public_observation"
        self.assertIn("permits only public", " ".join(fp.validate(d)))

    def test_must_not_out_of_scope(self):
        d = self.edit()
        d["features"][0]["status"] = "out_of_scope"
        self.assertIn("cannot be out_of_scope", " ".join(fp.validate(d)))

    def test_invalid_schema(self):
        d = self.edit()
        d["schema_version"] = True
        self.assertIn("schema_version", " ".join(fp.validate(d)))

    def test_bad_date(self):
        d = self.edit()
        d["sources"][0]["observed_on"] = "not a date"
        self.assertIn("observed_on", " ".join(fp.validate(d)))

    def test_nonobject(self):
        self.assertTrue(fp.validate([1, 2]))

    def test_unhashable_values_are_errors(self):
        for group, key in [("features", "status"), ("features", "priority"),
                           ("tests", "status"), ("sources", "kind"), ("evidence", "kind")]:
            d = self.edit()
            d[group][0][key] = {"bad": 1}
            self.assertTrue(fp.validate(d), (group, key))

    def test_corrupt_link(self):
        d = self.edit()
        d["flows"][0]["test_ids"] = ["TEST-999"]
        self.assertIn("unknown reference", " ".join(fp.validate(d)))

    def test_cases_do_not_claim_executed(self):
        s = fp.cases(self.doc)
        self.assertIn("Planning suggestions only", s)
        self.assertIn("Unicode", s)

    def test_fixture_csv(self):
        stream = io.StringIO()
        w = csv.writer(stream)
        w.writerow(["name", "quantity"])
        w.writerow(["Изюм", "2"])
        self.assertEqual(list(csv.reader(io.StringIO(stream.getvalue())))[1], ["Изюм", "2"])

    def test_scaffold_not_ready(self):
        d = fp.scaffold("Тестовый проект")
        self.assertTrue(fp.validate(d))
        self.assertEqual(d["project"], "Тестовый проект")

    def test_atomic_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            fp.create(p, fp.scaffold("first"))
            with self.assertRaises(fp.ManifestError):
                fp.create(p, fp.scaffold("second"))
            self.assertEqual(fp.load(p)["project"], "first")

    def test_atomic_refuses_parent_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "real"
            parent.mkdir()
            link = Path(tmp) / "link"
            try:
                link.symlink_to(parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            with self.assertRaises(fp.ManifestError):
                fp.create(link / "one.json", fp.scaffold("test"))

    @unittest.skipUnless(sys.platform == "win32", "Windows junction behavior")
    def test_atomic_refuses_parent_junction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.mkdir()
            junction = root / "junction"
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                                    capture_output=True, text=True, check=False)
            if result.returncode:
                self.skipTest(f"Could not create junction: {result.stderr or result.stdout}")
            try:
                with self.assertRaisesRegex(fp.ManifestError, "reparse point"):
                    fp.create(junction / "draft.json", fp.scaffold("unsafe"))
            finally:
                junction.rmdir()

    def test_read_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_text('{"project": "a", "project": "b"}', encoding="utf-8")
            with self.assertRaises(fp.ManifestError):
                fp.load(p)

    def test_read_size_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "manifest.json"
            p.write_bytes(b"x" * (fp.MAX_BYTES + 1))
            with self.assertRaises(fp.ManifestError):
                fp.load(p)

    def test_cli_validate_and_gate(self):
        cli = ROOT / "src" / "flow_parity.py"
        demo = ROOT / "examples" / "demo.json"
        a = subprocess.run([sys.executable, str(cli), "validate", str(demo), "--json"],
                           capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertTrue(json.loads(a.stdout)["valid"])
        b = subprocess.run([sys.executable, str(cli), "gate", str(demo), "--json"],
                           capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(b.returncode, 0, b.stderr)
        self.assertTrue(json.loads(b.stdout)["recorded_gate_pass"])

    def test_cli_draft_refuses_overwrite(self):
        cli = ROOT / "src" / "flow_parity.py"
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "TASK.json"
            a = subprocess.run([sys.executable, str(cli), "init", "--out", str(p), "--name", "Новый проект"],
                               capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(a.returncode, 0, a.stderr)
            b = subprocess.run([sys.executable, str(cli), "init", "--out", str(p), "--name", "other"],
                               capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(b.returncode, 2)
            self.assertEqual(fp.load(p)["project"], "Новый проект")


if __name__ == "__main__":
    unittest.main()
