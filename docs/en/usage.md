# Installation and usage

## Native skill (preferred)

Copy `.agents/skills/flow-parity/` into the target repository's `.agents/skills/` directory. Inspect an existing destination first. In a Codex session opened at the target repository, ask explicitly: `Use $flow-parity to map our own app's export flow and verify the local implementation.` No global Codex settings, paid API, server or Python are needed for the skill.

Do not assume automatic activation until a clean Codex session demonstrates it. If ScopeAnchor is installed already, keep it for task stopping/routing; FlowParity focuses on feature evidence and scenario QA.

## Offline CLI (optional)

Windows PowerShell from the FlowParity source checkout:

```powershell
py -3 src/flow_parity.py init --out task.json --name "Example"
py -3 src/flow_parity.py validate task.json --json
py -3 src/flow_parity.py cases examples/demo.json
py -3 src/flow_parity.py report examples/demo.json --json
py -3 src/flow_parity.py gate examples/demo.json --json
```

Ubuntu:

```bash
python3 src/flow_parity.py --help
python3 -m unittest discover -s tests -v
```

`task.json` is an incomplete draft. Fill the arrays, source permission notes, recorded evidence IDs and manual review fields before trying to gate it. To understand the required schema, read [the synthetic example](../../examples/demo.json) and [Architecture](architecture.md). Do not treat its recorded PASS as real app testing.

Use `cases` for planning only; output appears on standard output and is not saved. Redirect it yourself only if you intend to store the checklist in your project's existing QA documentation. Do not run any fuzzing or automated penetration testing against external targets.
