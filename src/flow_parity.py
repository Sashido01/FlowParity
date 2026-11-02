#!/usr/bin/env python3
"""FlowParity: offline, evidence-linked feature and journey acceptance checks.

No subprocess, network calls, or external Python packages.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

MAX_BYTES = 1_048_576
ID_PATTERNS = {"sources": r"SRC-\d{3,5}", "features": r"FEAT-\d{3,5}",
               "flows": r"FLOW-\d{3,5}", "tests": r"TEST-\d{3,5}",
               "evidence": r"EV-\d{3,5}"}
STATUS = {"planned", "partial", "verified", "blocked", "out_of_scope"}
TEST_STATUS = {"not_run", "passed", "failed", "blocked"}
PRIORITIES = ("must", "should", "could")


class ManifestError(ValueError):
    """The manifest cannot be parsed or does not conform to the contract."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    try:
        if path.stat().st_size > MAX_BYTES:
            raise ManifestError("Input exceeds the 1 MiB limit")
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            raise ManifestError("Input exceeds the 1 MiB limit")
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                          parse_constant=lambda n: (_ for _ in ()).throw(ManifestError(f"Non-finite JSON value: {n}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Cannot read manifest: {exc}") from exc


def _text(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip()) and len(v) <= 2000


def _ids(value: Any, known: set[str], label: str, errors: list[str], *, required: bool = False) -> None:
    if not isinstance(value, list) or (required and not value):
        errors.append(f"{label}: expected {'nonempty ' if required else ''}list")
        return
    if len(value) != len(set(str(x) for x in value)):
        errors.append(f"{label}: duplicate references")
    for item in value:
        if type(item) is not str or item not in known:
            errors.append(f"{label}: unknown reference {item!r}")


def _date(v: Any) -> bool:
    if not isinstance(v, str):
        return False
    try:
        return dt.date.fromisoformat(v).isoformat() == v
    except ValueError:
        return False


def validate(doc: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["Root must be a JSON object"]
    if type(doc.get("schema_version")) is not int or doc["schema_version"] != 1:
        errors.append("schema_version must be integer 1")
    if not _text(doc.get("project")):
        errors.append("project: nonempty string required")
    ref = doc.get("reference")
    if not isinstance(ref, dict) or not _text(ref.get("label")) or not isinstance(ref.get("basis"), str) or ref.get("basis") not in {"owned", "authorized", "public_observation"}:
        errors.append("reference: label and basis (owned|authorized|public_observation) required")
    groups: dict[str, list[dict[str, Any]]] = {}
    known: dict[str, set[str]] = {}
    for group, pattern in ID_PATTERNS.items():
        items = doc.get(group)
        if not isinstance(items, list) or len(items) > 1000:
            errors.append(f"{group}: expected list with at most 1000 entries")
            items = []
        groups[group] = []
        known[group] = set()
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{group}[{i}]: expected object")
                continue
            ident = item.get("id")
            if not isinstance(ident, str) or not re.fullmatch(pattern, ident):
                errors.append(f"{group}[{i}]: invalid id")
                continue
            if ident in known[group]:
                errors.append(f"{group}: duplicate id {ident}")
                continue
            known[group].add(ident)
            groups[group].append(item)

    if not groups["features"]:
        errors.append("features: at least one feature required")
    for s in groups["sources"]:
        p = f"source {s['id']}"
        if not isinstance(s.get("kind"), str) or s.get("kind") not in {"owned", "authorized", "public"}:
            errors.append(f"{p}: kind must be owned|authorized|public")
        if not _text(s.get("locator")):
            errors.append(f"{p}: locator required")
        if not _date(s.get("observed_on")):
            errors.append(f"{p}: observed_on must be YYYY-MM-DD")
        if s.get("kind") == "authorized" and not _text(s.get("permission_note")):
            errors.append(f"{p}: authorized source requires permission_note")
        if isinstance(ref, dict) and ref.get("basis") == "public_observation" and s.get("kind") != "public":
            errors.append(f"{p}: public_observation permits only public sources")
    for e in groups["evidence"]:
        p = f"evidence {e['id']}"
        if not isinstance(e.get("kind"), str) or e.get("kind") not in {"test", "manual", "artifact"} or not _text(e.get("locator")):
            errors.append(f"{p}: kind (test|manual|artifact) and locator required")
        if not _text(e.get("summary")):
            errors.append(f"{p}: summary required")
    for f in groups["features"]:
        p = f"feature {f['id']}"
        if not _text(f.get("title")) or not isinstance(f.get("priority"), str) or f.get("priority") not in PRIORITIES or not isinstance(f.get("status"), str) or f.get("status") not in STATUS:
            errors.append(f"{p}: title, priority and status required")
        _ids(f.get("source_ids"), known["sources"], p + " source_ids", errors,
             required=f.get("status") == "verified")
        _ids(f.get("evidence_ids"), known["evidence"], p + " evidence_ids", errors,
             required=f.get("status") == "verified")
        if f.get("status") == "out_of_scope":
            if f.get("priority") == "must":
                errors.append(f"{p}: must-have cannot be out_of_scope")
            if not _text(f.get("notes")):
                errors.append(f"{p}: out_of_scope requires a reason")
    flow_ids = known["flows"]
    test_ids = known["tests"]
    for flow in groups["flows"]:
        p = f"flow {flow['id']}"
        if not _text(flow.get("title")) or not _text(flow.get("expected")):
            errors.append(f"{p}: title and expected outcome required")
        steps = flow.get("steps")
        if not isinstance(steps, list) or not steps or any(not _text(s) for s in steps):
            errors.append(f"{p}: nonempty steps list required")
        _ids(flow.get("feature_ids"), known["features"], p + " feature_ids", errors, required=True)
        _ids(flow.get("test_ids"), test_ids, p + " test_ids", errors, required=True)
    for test in groups["tests"]:
        p = f"test {test['id']}"
        if not isinstance(test.get("flow_id"), str) or test.get("flow_id") not in flow_ids:
            errors.append(f"{p}: unknown flow_id")
        if not isinstance(test.get("status"), str) or test.get("status") not in TEST_STATUS:
            errors.append(f"{p}: invalid status")
        _ids(test.get("evidence_ids"), known["evidence"], p + " evidence_ids", errors,
             required=test.get("status") == "passed")
    for flow in groups["flows"]:
        for test_id in flow.get("test_ids", []) if isinstance(flow.get("test_ids"), list) else []:
            matching = [t for t in groups["tests"] if t.get("id") == test_id]
            if matching and matching[0].get("flow_id") != flow["id"]:
                errors.append(f"flow {flow['id']}: test {test_id} points to another flow")
    review = doc.get("review")
    if not isinstance(review, dict) or type(review.get("approved_for_release")) is not bool or \
       not isinstance(review.get("security_review"), str) or review.get("security_review") not in {"not_run", "passed", "failed"} or \
       not isinstance(review.get("license_review"), str) or review.get("license_review") not in {"not_run", "passed", "failed"}:
        errors.append("review: approved_for_release (boolean), security_review and license_review required")
    return errors


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    counts = {p: {"total": 0, "verified": 0, "partial": 0, "blocked": 0} for p in PRIORITIES}
    blockers: list[str] = []
    for f in doc["features"]:
        if f["status"] == "out_of_scope":
            continue
        c = counts[f["priority"]]
        c["total"] += 1
        if f["status"] == "verified":
            c["verified"] += 1
        if f["status"] == "partial":
            c["partial"] += 1
        if f["status"] == "blocked":
            c["blocked"] += 1
        if f["priority"] == "must" and f["status"] != "verified":
            blockers.append(f"{f['id']}: must-have not verified ({f['status']})")
    if not counts["must"]["total"]:
        blockers.append("No must-have features defined")
    if not doc["flows"]:
        blockers.append("No user flows recorded")
    if not doc["tests"]:
        blockers.append("No tests recorded")
    flow_feature_ids = {ref_id for flow in doc["flows"] for ref_id in flow["feature_ids"]}
    for f in doc["features"]:
        if f["priority"] == "must" and f["id"] not in flow_feature_ids:
            blockers.append(f"{f['id']}: must-have not covered by a flow")
    for t in doc["tests"]:
        if t["status"] != "passed":
            blockers.append(f"{t['id']}: test not passed ({t['status']})")
    for flow in doc["flows"]:
        if not flow["test_ids"]:
            blockers.append(f"{flow['id']}: no tests")
    r = doc["review"]
    if not r["approved_for_release"]:
        blockers.append("Release approval not recorded")
    if r["security_review"] != "passed":
        blockers.append("Security review not passed")
    if r["license_review"] != "passed":
        blockers.append("License review not passed")
    return {"project": doc["project"], "coverage": counts, "recorded_gate_pass": not blockers,
            "blockers": blockers,
            "notice": "Checks recorded evidence links and attestations, not real-world correctness."}


def scaffold(name: str) -> dict[str, Any]:
    return {"schema_version": 1, "project": name,
            "reference": {"label": "", "basis": "owned", "notes": ""},
            "sources": [], "features": [], "flows": [], "tests": [], "evidence": [],
            "review": {"approved_for_release": False, "security_review": "not_run", "license_review": "not_run"}}


def _is_link_or_reparse_point(path: Path) -> bool:
    """Reject symlinks and Windows reparse points, including junctions on 3.10."""
    try:
        if path.is_symlink():
            return True
        if os.name != "nt":
            return False
        attributes = path.lstat().st_file_attributes
    except (FileNotFoundError, NotADirectoryError):
        return False
    except (AttributeError, OSError):
        return True  # Fail closed when the path cannot be inspected safely.
    return bool(attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT


def create(path: Path, data: dict[str, Any]) -> None:
    # Protect existing files including links. Parent directories must already exist.
    parents = list(path.parents)
    if _is_link_or_reparse_point(path) or any(_is_link_or_reparse_point(parent) for parent in parents):
        raise ManifestError("Refusing to write through symlink or reparse point")
    encoded = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(encoded)
    except FileExistsError as exc:
        raise ManifestError(f"File already exists: {path}") from exc
    except OSError as exc:
        raise ManifestError(f"Cannot create file: {exc}") from exc


def cases(doc: dict[str, Any]) -> str:
    rows = ["# FlowParity QA cases", "", "Planning suggestions only. Run tests against the *local implementation*, not a third-party application.", ""]
    for flow in doc["flows"]:
        rows.extend([f"## {flow['id']} — {flow['title']}", "", "Happy path:"])
        rows.extend(f"{i}. {step}" for i, step in enumerate(flow["steps"], 1))
        rows.extend([f"Expected: {flow['expected']}", "", "Applicability checklist (mark N/A with reason):",
                     "- [ ] Empty and invalid inputs", "- [ ] Unicode and long inputs",
                     "- [ ] Repeated action / interrupted flow", "- [ ] Restricted access and data separation",
                     "- [ ] Offline/restart or persistence (if applicable)",
                     "- [ ] Keyboard/accessibility and supported viewport", ""])
    if not doc["flows"]:
        rows.append("No flows recorded; QA coverage has not been established.")
    return "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FlowParity: offline evidence-linked QA contracts")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create an intentionally incomplete JSON manifest")
    init.add_argument("--out", required=True, type=Path)
    init.add_argument("--name", required=True)
    for cmd in ("validate", "report", "gate", "cases"):
        p = sub.add_parser(cmd)
        p.add_argument("manifest", type=Path)
        if cmd in ("validate", "report", "gate"):
            p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            if not _text(args.name):
                raise ManifestError("--name must be a nonempty project title (max 2000 chars)")
            create(args.out, scaffold(args.name))
            print(f"Created incomplete draft: {args.out}")
            return 0
        doc = load(args.manifest)
        errors = validate(doc)
        if args.command == "validate":
            result = {"valid": not errors, "errors": errors}
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("VALID" if not errors else "INVALID\n" + "\n".join(errors))
            return 0 if not errors else 2
        if errors:
            raise ManifestError("Invalid manifest:\n" + "\n".join(errors))
        if args.command == "cases":
            print(cases(doc), end="")
            return 0
        result = evaluate(doc)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Project: {result['project']}")
            for name, counts in result["coverage"].items():
                print(f"{name}: {counts['verified']}/{counts['total']} verified; {counts['partial']} partial; {counts['blocked']} blocked")
            print("RECORDED GATE: PASS" if result["recorded_gate_pass"] else "RECORDED GATE: BLOCKED")
            for blocker in result["blockers"]:
                print(f"- {blocker}")
            print(result["notice"])
        return 0 if args.command == "report" or result["recorded_gate_pass"] else 3
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
