[English](CHANGELOG.md) | [Русский](CHANGELOG.ru.md)

# Changelog

## 0.0.1 — 2026-11-02

- Refused manifest creation through Windows reparse points, including junctions on Python 3.10; added a Windows junction regression check.
- Kept Windows reparse attributes out of POSIX path checks after Ubuntu CI exposed a mode-bit collision; refreshed CI actions to current Node 24 releases and verified their full SHAs.
- Restored the existing public README commit as the base of local history and completed the bilingual release documentation.

## 0.0.0 — 2026-11-02

- Added original, native Codex `flow-parity` skill with concise permissions, reconnaissance, QA and native-stack references.
- Added offline JSON manifest CLI with fail-closed syntax/reference checks, feature coverage, written release gate and QA-case suggestions.
- Added test suite, synthetic fixture, bilingual documentation, local Git workflow and Windows/Ubuntu CI configuration.
- Scope: functional analysis and evidence organization only, not an app clone engine, legal certification or end-to-end app test runner.
