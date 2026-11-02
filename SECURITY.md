[English](SECURITY.md) | [Русский](SECURITY.ru.md)

# Security

Please do **not** report exploitable issues or secrets in public GitHub issues. Use the repository's **Security → Report a vulnerability** workflow for private reports. If that workflow is unavailable, contact the maintainer privately using a channel they explicitly publish; no private email address is asserted here.

The CLI runs offline, performs no shell/network execution, and refuses to overwrite existing manifests. It does not sandbox local inputs, inspect external evidence files, prevent all local filesystem race conditions or independently certify an app. Do not run it against untrusted repositories with elevated privileges.

Source apps are observation-only unless explicitly owned/authorized. Never test third-party systems for vulnerabilities without permission. Use local targets for QA and keep secrets/private research outside Git.
