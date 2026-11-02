# Development

Python 3.10+ is required only for the optional offline CLI. No install or third-party dependencies. On Windows use `py -3`, on Ubuntu use `python3`.

From repository root:

```console
python -m unittest discover -s tests -v
python -m compileall -q src
python src/flow_parity.py validate examples/demo.json --json
python src/flow_parity.py gate examples/demo.json --json
```

Use native Git with small descriptive commits. The GitHub Actions workflow tests on Windows and Ubuntu with Python 3.10 and 3.13, with pinned action SHAs and least-privilege permissions. Hosted CI execution is not verified until GitHub returns completed successful runs for the final commit.

Update English and Russian docs together; use `NOT_VERIFIED` for untested platforms or Codex activation. Do not add runtime dependencies, CI deployment, telemetry or a custom server without a demonstrated need.
