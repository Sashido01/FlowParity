# Architecture

FlowParity has **two independent components**:

1. `.agents/skills/flow-parity/`: a native Codex Agent Skill with a short `SKILL.md`, optional agent display metadata and four lazily read workflow references. It uses the host project's existing tools; it is not a coding agent, browser automation service or build system by itself.
2. `src/flow_parity.py`: optional, offline Python 3.10+ standard-library helper. It reads a UTF-8 JSON manifest (≤1 MiB) and exposes `init`, `validate`, `cases`, `report`, `gate`. No network, subprocess, shell, dependencies or telemetry. `init` is the only write operation and refuses existing paths.

## Manifest contract

The `schema_version: 1` document contains `project`, `reference`, `sources`, `features`, `flows`, `tests`, `evidence`, and `review`. Each linked object uses a unique type-prefixed ID such as `SRC-001`, `FEAT-001`, `FLOW-001`, `TEST-001`, `EV-001`.

- Reference `basis`: `owned`, `authorized`, or `public_observation`. Authorized sources require a permission note; public-observation reference cannot claim owned/private inputs.
- Feature priority: `must`, `should`, `could`; status: `planned`, `partial`, `verified`, `blocked`, `out_of_scope`. Verified features require both valid source IDs and evidence IDs. Must-have cannot be marked out of scope.
- Each flow has steps, expected result, mapped features and test IDs. Passed tests require evidence IDs.
- `review` records booleans and manual `security_review`/`license_review` attestations; the tool cannot evaluate whether a review actually took place.

`gate` passes only when a nonempty set of must-have features are verified and mapped, flows/tests exist and all listed tests are passed, and the review records approvals. `should`/`could` remain informational. This is a **recorded gate**, not actual execution or certification. A deliberately false record can pass; independent verification remains mandatory.

## Error contract

Exit codes: `0` for successful command (including informational `report` on blocked manifests), `2` for invalid input or filesystem error, `3` for a valid but blocked `gate`.

Implementation follows the host project's native stack and logging; no duplicate source-of-truth documents are required. See [Usage](usage.md), [Security](security.md).
