[English](README.md) | [Русский](README.ru.md)

# FlowParity

**Native Codex skill for permission-respecting application analysis, original UX reconstruction, and evidence-linked feature verification.**

**Version:** 0.0.1 · **License:** MIT · **Runtime:** Codex for the skill, Python 3.10+ for the optional offline CLI.

FlowParity is **not** a tool for extracting another app's code, brand, private API, data, or copyrighted assets. It helps engineers understand allowed user journeys, implement equivalent capabilities in their **existing native stack**, and verify the local result. No API keys, server, model subscription or third-party Python libraries required.

## What it does

- Records permitted sources, observed user flows, feature priorities, and evidence without inventing behavior.
- Keeps functional parity separate from visual imitation or ownership of proprietary design.
- Guides native implementation in existing HTML5/Node, Rust/Slint/SQLite, and Windows workflows.
- Helps prepare local negative, accessibility, privacy and persistence checks.
- Provides a small offline `init` / `validate` / `cases` / `report` / `gate` CLI for optional JSON traceability.
- Stops when actual acceptance evidence meets the agreed goal; avoids unnecessary task and artifact proliferation.

## Install the Codex skill

Copy the **whole** `.agents/skills/flow-parity/` folder into a target repository's `.agents/skills/` folder. Compare any existing destination before changing it. The skill can also be used in this repo directly. In Codex, explicitly invoke:

```text
Use $flow-parity to study our permitted application flow and independently implement and verify it.
```

The skill is repository-scoped and does not change global Codex settings, authentication or MCP services. Whether automatic invocation occurs in your specific Codex host must be tested there; the current repo has only static skill checks.

## Optional CLI

The CLI is fully offline and only writes to an explicitly named new path with `init`:

```powershell
# PowerShell (Windows) — from repo root
py -3 src/flow_parity.py --help
py -3 src/flow_parity.py init --out task.json --name "My app"
py -3 src/flow_parity.py validate task.json
py -3 src/flow_parity.py cases examples/demo.json
py -3 src/flow_parity.py report examples/demo.json
py -3 src/flow_parity.py gate examples/demo.json
```

```bash
# Ubuntu
python3 -m unittest discover -s tests -v
python3 src/flow_parity.py report examples/demo.json --json
```

`examples/demo.json` is **synthetic test data** and intentionally has recorded approval. Its successful gate is **not** evidence that any real application passed QA. The gate only evaluates the manifest, including approval fields supplied by its author; it does not check external evidence files or independently conduct a security review. New manifests are intentionally incomplete and fail validation until filled.

## How to work

1. Verify observation rights. Choose one local user flow and the smallest useful boundary.
2. Map observed inputs, outputs, edge cases, permissions, and evidence with dates and source IDs.
3. Implement in the project's existing stack, using original UI assets and copy.
4. Test the **local implementation**, record actual results, and mark unknowns `NOT_VERIFIED`.
5. Report completion only when evidence matches scope. Publishing needs explicit approval.

Ready to publish? See [Publishing](docs/en/publishing.md).

Full English docs: [Usage](docs/en/usage.md), [Architecture](docs/en/architecture.md), [Safety](docs/en/security.md), [Development](docs/en/development.md). Russian equivalents are linked from [README.ru.md](README.ru.md).

## Scope and limits

This project has no browser automation engine, app clone generator, file downloader, image diff, source-code crawler, model runner or automatic publishing. The Python CLI checks record structure, references and written release attestations, **not** application equivalence. Independent functional test execution and OS-specific Codex activation are `NOT_VERIFIED` until run in the target environment. No measured quota savings are claimed.

Compatible with a host repo's `AGENTS.md` and its own skills. If ScopeAnchor is present, retain its existing task completion process rather than duplicating it.

## Community

[Contributing](CONTRIBUTING.md) · [Security reporting](SECURITY.md) · [Provenance](docs/PROVENANCE.md) · [Changelog](CHANGELOG.md) · [MIT License](LICENSE).
