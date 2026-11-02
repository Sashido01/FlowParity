[English](CONTRIBUTING.md) | [Русский](CONTRIBUTING.ru.md)

# Contributing

Open a focused issue describing a concrete deficiency, reproduction, expected outcome, and proposed boundary. Never paste third-party proprietary material, screenshots with personal data, credentials, or private targets. All contributions must be independently written or legally reusable, with provenance and compatible licenses.

Use Python 3.10+ and the standard library. Run `python -m unittest discover -s tests -v` and `python -m compileall -q src`; keep new regression tests. Update English and Russian docs together. Small, descriptive commits are preferred. Do not claim release readiness from a passing manifest gate alone.

Maintainers review PRs before merging; opening a PR does not authorize shipping to a production service.
