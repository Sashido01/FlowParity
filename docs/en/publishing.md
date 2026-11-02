# Publishing and release checks

FlowParity is published in `Sashido01/FlowParity`. The public repository began with a README-only commit; local work must retain that commit as an ancestor. Never force-push or publish local research, credentials, screenshots, private notes, or a Git bundle.

## Before publishing

1. Review the staged paths and commit history. Confirm the base is the current `origin/main` and the working tree contains only intended public files.
2. Run the documented tests, compilation, CLI checks, link checks, and `git diff --check`. Record exact outcomes; hosted Windows/Codex behavior remains unverified until actually observed.
3. Check all commits to be pushed for secrets and private research. Keep the synthetic example clearly labeled.
4. Push with ordinary `git push origin main`; resolve divergence with normal Git operations and review the resulting history. Never force-push.
5. Open the final commit's Actions runs and verify each configured operating system and Python version. A workflow file or queued run is not a passing result.
6. Inspect the public tree, rendered README, relative links, repository description/topics and available security settings.

## Version and release

Keep `VERSION`, both READMEs and both changelogs aligned. Use a patch increment for a compatible first checked release. Create a GitHub Release only after its exact tag contents and acceptance evidence are reviewed; local tests alone do not establish stability or application parity.

## Current verification boundaries

The CLI evaluates author-recorded evidence references and release attestations. It does not open evidence files, run the target app, activate Codex skills, or independently establish legal rights. Report any unavailable Windows, hosted CI, or Codex checks as `NOT_VERIFIED`.
